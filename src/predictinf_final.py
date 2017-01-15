import gfa
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
from generate_data import *
from sklearn.metrics import mean_squared_error

groupmax=40 # maximum group number
groupmin=4  # minimum group number
groupcounter=2
RMSE = np.zeros([(groupmax-groupmin)//groupcounter+1,1])  # sequence of RMSE from M=4 to M=100
trialmax=50 # trial number for average

def run_RMSE(rank, save=True):
    for changegroup in range(0,(groupmax-groupmin)//groupcounter+1,1):
            # Create Corentin's artifical data set corresponding to Experiment C (original paper)
            Leave = 0 # group which we will leave for prediction

            K = 18 #factors
            numM = changegroup*groupcounter+groupmin # number of groups
            Dm = 7 # dimension of each group
            D = Dm*np.ones(numM,dtype=int) #groups
            scalerD=Dm*numM
            N = 30 #samples
            R = 4#min(K,numM)#4 #rank
            if rank == None:
                R = numM

            # generate indepdent datasets
            for trial in range(0,trialmax,1):
                    X, W, Z, alpha, Tau = generation(N, K, D, R,constrain_W=10) # independent trial = data is generated at each trial

                    # Run GFA

                    g = gfa.GFA_rep(X,D, n=1, debug_iter=False, rank=R, factors=K,optimize_method="l-bfgs-b", debug=False, max_iter=10)

                   # while W.max()>10000:
                    #        g = gfa.GFA_rep(X,D, n=1, debug_iter=False, rank=R, factors=K,optimize_method="l-bfgs-b", debug=False, max_iter=100)

                    # Calculate leave-one-prediction
                    print(changegroup)
                    print(trial)
                    Yminus=np.zeros([N,0]) # K x 0 (matrix will be expanded afterward)

                    T=np.zeros([scalerD-Dm,scalerD-Dm]) # D-Dm x D-Dm

                    Wminus=np.zeros([K,0]) # K x 0 (matrix will be expanded afterward)
                    Sigma=np.identity(K) # K x K
                    Wm=g.E_W(Leave) # K x Dm

                    count=0
                    for i in range(0,numM,1):
                            if i!=Leave:
                                    count=count+1
                                    Yminus=np.c_[Yminus,X.T[:,i*Dm:(i+1)*Dm]]  # N x D-Dm
                                    T[(count-1)*Dm:count*Dm,(count-1)*Dm:count*Dm]=g.E_tau(i)*np.identity(Dm) # diag({<tau_j>I_Dj}_j\neqm)

                                    Sigma=Sigma+g.E_tau(i)*g.E_WW(i) # I_k+\sum_{j\neqm}<tau_j><W^(j){W^(j)}^{T}>
                                    Wminus=np.c_[Wminus,g.E_W(i)] # Finally K x D-Dm

                    Xmpre=Yminus @ T @ Wminus.T @ np.linalg.pinv(Sigma) @ Wm  # (N x D-Dm)x(D-Dm x D-Dm)x(D-Dm x K)x(K x K)x(K x Dm)=(K x Dm)

                    preerr=np.sqrt(np.sum(((X.T[:,Leave*Dm:(Leave+1)*Dm]-Xmpre)/(np.max(X.T[:,Leave*Dm:(Leave+1)*Dm])-np.min(X.T[:,Leave*Dm:(Leave+1)*Dm])))**2))  # squared error of the prediction = scaler
                    print(preerr)
                    RMSE[changegroup]=RMSE[changegroup]+preerr  # summing (devided by trialmax afterward)

                    if save:
                        np.save("res/backup-{}.npy".format(rank), RMSE)

    return RMSE/trialmax  # averaging

if __name__ == '__main__':
    RMSE_full = run_RMSE(None)
    RMSE_4 = run_RMSE(4)

    # Visualize the result
    plt.figure()

    red_patch = mpatches.Patch(color='red', label='R = 4')
    blue_patch = mpatches.Patch(color='blue', label='R = M')
    plt.legend(handles=[red_patch])
    plt.plot(range(groupmin,groupmax+1,groupcounter),RMSE_4,color='r',linewidth=3)
    plt.plot(range(groupmin,groupmax+1,groupcounter),RMSE_full,color='b',linewidth=3)

    # plt.title("Prediction RMSE against group number")
    plt.ylabel("Prediction RMSE")
    plt.xlabel("Groups")
    plt.savefig('figure4a.eps')
    plt.show()
