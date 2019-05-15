import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import FormatStrFormatter
import time
import yaml
from lib.experiment import Experiment
from lib.solver import Solver
from lib.solvers.anls_bpp import ANLSBPP
from lib.solvers.hals import HALS
from lib.solvers.mu import MU
from lib.solvers.sparse_hals import SparseHALS
from lib.solvers.sparse_anls_bpp import SparseANLSBPP
from lib.solvers.sparse_hoyer import SparseHoyer


def generate_synthetic_data(n, m, r, l0):
    '''
    generates synthetic sparse dataset
    '''
    l_list = np.ceil(m * l0).astype(np.int32)
    length = len(l_list)
    W = np.abs(np.random.normal(2, scale=3, size=(n, r, len(l_list))))
    W /= np.linalg.norm(W, axis = 0)
    print(W[:, :, 0])

    H = np.zeros((r, m, length))
    X = np.zeros((n, m, length))
    index = 0
    for l in l_list:
        x = np.zeros((r, m))
        for i in range(r):
            nonzero = np.random.randint(m, size=(l,))
            random = np.abs(np.random.normal(size=(m,), scale=10))
            x[i, nonzero] = random[nonzero]
        H[:, :, index] = x.copy()
        X[:, :, index] = np.matmul(W[:, :, index], H[:, :, index])
        index += 1
    return X, W, H


def peharz_experiment():
    '''
    runs the peharz experiment and generates its plots
    '''
    # load experiment config file
    config = yaml.safe_load(open('./config/dev.yml'))
    config['clip'] = False # otherwise methods diverge?
    experiment_config = yaml.safe_load(open('./experiments/peharz.yml'))
    name = 'peharz'
    solvers = experiment_config['solver_list']
    # generate data
    n = experiment_config['n']
    m = experiment_config['m']
    r = experiment_config['r']
    l0 = np.array([0.2, 0.3, 0.5, 0.7, 0.9])
    X, W, H = generate_synthetic_data(n, m, r, l0)
    print('Data generated, rank of X: ', np.linalg.matrix_rank(X[:, :, 0]))
    accuracy = np.zeros((len(l0), len(solvers)))
    total = [np.zeros((len(experiment_config['solver_list']), 0)) for feature in experiment_config['plot']]
    for i in range(len(l0)):
        # generate experiment object
        experiment = Experiment(config, X[:, :, i], experiment_config)
        experiment.run()
        summary = experiment.get_summary()
        for i, feature in enumerate(experiment_config['plot']):
            a = summary[feature]
            a = np.array(a).reshape((len(a), 1))
            total[i] = np.hstack((total[i], a))

        accuracy[i, :] = np.array(summary['error'])

    # plotting last experiment
    for i, feature in enumerate(experiment_config['plot']):
        fig = plt.figure(figsize=(6, 4))
        ax0 = fig.add_subplot(111)
        color = ['r', 'g', 'b', 'cyan', 'k']
        ax0.set_xlabel('$\ell_0$')
        for j in range(total[i].shape[0]):
            ax0.plot(l0, total[i][j, :], color=color[j], label = solvers[j], linestyle='--', markersize=20, marker='.')
        ax0.yaxis.set_major_formatter(FormatStrFormatter('%g'))
        ax0.xaxis.set_major_formatter(FormatStrFormatter('%g'))
        ax0.get_yaxis().set_tick_params(which='both', direction='in')
        ax0.get_xaxis().set_tick_params(which='both', direction='in')
        ax0.grid()
        ax0.set_ylabel(feature)
        #ax0.legend()
        #ax0.set_xscale('log')
        #ax0.set_yscale('log')
        s = '_' + str(n) + '_' + str(m) + '_' + str(r)
        fig.savefig('./experiments/' + name + '/' + feature + s + '.pgf', bbox_inches='tight')
        fig.savefig('./experiments/' + name + '/' + feature + s + '.pdf', bbox_inches='tight')


def faces_experiment():
    '''
    applies NMF to the faces dataset and generates an image
    '''
    pass

