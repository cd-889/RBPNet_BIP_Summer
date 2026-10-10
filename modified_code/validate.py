import os
import torch
import numpy as np
from scipy.stats import pearsonr
from RBPNet import *
from metrics import rbpnet_metrics, pearson_corr
from module import Module

import seqpro as sp
import seqdata as sd
import sys
from pathlib import Path

from yaml import load
try:
    from yaml import CLoader as Loader
except ImportError:
    from yaml import Loader

import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from tqdm import tqdm


def find_latest_ckp(log_directory):
    checkpoints = list((Path(log_directory) / 'checkpoints').glob("*.ckpt"))
    checkpoint_epochs = [
        int(i.name.split('=')[1].split('-')[0]) for i in checkpoints
    ]
    latest_checkpoint = [
        x for _, x in sorted(zip(checkpoint_epochs, checkpoints))
    ][-1]

    print(latest_checkpoint)
    return latest_checkpoint


def predict(model, x, batch_size=128, verbose=True):
    with torch.no_grad():
        device = model.device
        model.eval()

        if isinstance(x, np.ndarray):
            x = torch.from_numpy(x.astype(np.float32))

        outs = []
        pis = []

        for _, i in tqdm(
            enumerate(range(0, len(x), batch_size)),
            desc="Predicting on batches",
            total=len(x) // batch_size,
            disable=not verbose,
        ):
            batch = x[i:i + batch_size].to(device)

            # outputs:
            # 0 -> eCLIP_profile
            # 1 -> signal_profile
            # 2 -> control_profile
            # 3 -> mixing_coefficient
            outputs = model.arch(batch)

            out = outputs[0].detach().cpu()
            outs.append(out)

            pi = outputs[3].detach().cpu()
            pis.append(pi)

        return torch.cat(outs), torch.cat(pis)


if __name__ == '__main__':

    skipper_config = sys.argv[1]
    exp = sys.argv[2]
    data_dir = Path(sys.argv[3])
    log_dir = Path(sys.argv[4])

    mask = 100

    try:
        os.mkdir(log_dir / 'valid')
    except Exception as e:
        print(e)

    config = load(open(skipper_config), Loader=Loader)
    skipper_dir = Path(config['WORKDIR'])

    checkpoint = find_latest_ckp(log_dir)

    # load model
    module = Module.load_from_checkpoint(
        checkpoint,
        arch=RBPNet(mask=mask)
    )

    ####################################
    # Training curve
    ####################################

    metric_df = pd.read_csv(log_dir / 'metrics.csv')

    f, axes = plt.subplots(1, 2, figsize=(8, 3))

    metric_df.plot.scatter(
        x='epoch',
        y='train_eCLIP_loss_epoch',
        ax=axes[0],
        color='grey'
    )

    metric_df.plot.scatter(
        x='epoch',
        y='val_eCLIP_loss_epoch',
        ax=axes[0],
        color='tomato'
    )

    metric_df.plot.scatter(
        x='epoch',
        y='train_eCLIP_profile_pearson_epoch',
        ax=axes[1],
        color='grey'
    )

    metric_df.plot.scatter(
        x='epoch',
        y='val_eCLIP_profile_pearson_epoch',
        ax=axes[1],
        color='tomato'
    )

    sns.despine()
    plt.tight_layout()
    plt.savefig(log_dir / 'valid' / 'training_curve.pdf')
    plt.close()


    ####################################
    # Prediction on test set
    ####################################

    test_sdata = sd.open_zarr(
        os.path.join(data_dir, 'test.zarr')
    ).load()

    X = sp.ohe(
        test_sdata["seq"].values[..., 32:-32],
        alphabet=sp.alphabets.DNA
    ).transpose(0, 2, 1)

    y_pred, pis = predict(module, X)


    y_clip = torch.tensor(
        test_sdata["signal"].values[..., 32:-32].astype("float32"),
        dtype=torch.float32
    )

    # total counts
    y_total = torch.sum(y_clip, axis=1).unsqueeze(1)

    # expected counts from profile prediction
    probs = torch.nn.functional.softmax(y_pred, dim=1)
    expected_counts = probs * y_total

    pearsons = pearson_corr(
        expected_counts,
        y_clip
    ).detach().numpy()


    ####################################
    # Save metrics
    ####################################

    test_metrics = pd.DataFrame({
        'profile_pearsons': pearsons,
        'pi': pis.squeeze(),
        'n_IP': torch.from_numpy(test_sdata['n_IP'].values),
        'n_IN': torch.from_numpy(test_sdata['n_IN'].values),
        'gc_fraction': torch.from_numpy(test_sdata['gc_fraction'].values),
        'name': test_sdata['name'].values,
        'strand': test_sdata['strand'].values,
    })

    test_metrics['total'] = (
        test_metrics['n_IP'] +
        test_metrics['n_IN']
    )


    data_output = {}

    for nread in [10, 50, 100, 200]:
        subset = test_metrics[
            test_metrics['total'] > nread
        ]

        data_output[
            f'mean profile_pearson(total>{nread})'
        ] = subset['profile_pearsons'].mean()

        data_output[
            f'std profile_pearson(total>{nread})'
        ] = subset['profile_pearsons'].std()


    pd.Series(data_output).to_csv(
        log_dir / 'valid' / 'test_data_metric.csv'
    )


    ####################################
    # Correlation plot
    ####################################

    f, ax = plt.subplots(1, 1, figsize=(4, 3))

    sns.histplot(
        data=test_metrics,
        x='total',
        y='profile_pearsons',
        ax=ax
    )

    sns.regplot(
        data=test_metrics,
        x='total',
        y='profile_pearsons',
        scatter=False,
        ax=ax,
        lowess=True
    )

    ax.set_xlim(0, 1000)

    sns.despine()
    plt.tight_layout()
    plt.savefig(
        log_dir / 'valid' / 'correlation_plot.pdf'
    )
    plt.close()


    ####################################
    # Correlation with reproducible windows
    ####################################

    reproducible_enriched_windows = pd.read_csv(
        skipper_dir /
        f'output/reproducible_enriched_windows/{exp}.reproducible_enriched_windows.tsv.gz',
        sep='\t'
    )

    merged = pd.merge(
        test_metrics,
        reproducible_enriched_windows,
        left_on='name',
        right_on='name'
    )

    # Keep this section available for future analyses
    # with pi/enrichment correlations if desired.