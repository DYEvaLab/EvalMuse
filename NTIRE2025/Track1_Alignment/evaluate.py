#!/usr/bin/env python
import sys
import os
import os.path
import json
import numpy as np
import scipy.stats
from scipy.optimize import curve_fit
from sklearn.metrics import mean_squared_error

def logistic_func(X, bayta1, bayta2, bayta3, bayta4):
    # 4-parameter logistic function
    logisticPart = 1 + np.exp(np.negative(np.divide(X - bayta3, np.abs(bayta4))))
    yhat = bayta2 + np.divide(bayta1 - bayta2, logisticPart)
    return yhat

def compute_metrics(y_pred, y):
    '''
    compute metrics btw predictions & labels
    '''
    # compute SRCC & KRCC
    SRCC = scipy.stats.spearmanr(y, y_pred)[0]
    try:
        KRCC = scipy.stats.kendalltau(y, y_pred)[0]
    except:
        KRCC = scipy.stats.kendalltau(y, y_pred, method='asymptotic')[0]

    # logistic regression btw y_pred & y
    beta_init = [np.max(y), np.min(y), np.mean(y_pred), np.std(y_pred)]
    popt, _ = curve_fit(logistic_func, y_pred, y, p0=beta_init, maxfev=int(1e8))
    y_pred_logistic = logistic_func(y_pred, *popt)

    # compute PLCC RMSE
    PLCC = scipy.stats.pearsonr(y, y_pred_logistic)[0]
    RMSE = np.sqrt(mean_squared_error(y, y_pred))
    return SRCC, KRCC, PLCC, RMSE

def calculate_score(truth, submission):
    truth = sorted(truth, key=lambda x: x['img_path'])
    submission = sorted(submission, key=lambda x: x['img_path'])
    overall_score_gt = []
    overall_score_sub = []

    ele_score_gt = []
    ele_score_sub = []
    for i in range(len(truth)):
        overall_score_gt.append(truth[i]['total_score'])
        overall_score_sub.append(submission[i]['total_score'])
        for ele in truth[i]['element_score'].keys():
            ele_score_gt.append(truth[i]['element_score'][ele])
            ele_score_sub.append(submission[i]['element_score'][ele])
    SRCC, KRCC, PLCC, RMSE = compute_metrics(overall_score_gt, overall_score_sub)

    ele_score_gt = np.array(ele_score_gt)
    ele_score_sub = np.array(ele_score_sub)
    ele_score_gt = ele_score_gt>=0.5
    ele_score_sub = ele_score_sub>=0.5
    acc = np.sum(ele_score_gt==ele_score_sub)/len(ele_score_gt)
    return SRCC, PLCC, acc


input_dir = sys.argv[1]
output_dir = sys.argv[2]

submit_dir = os.path.join(input_dir, 'res')
truth_dir = os.path.join(input_dir, 'ref')

if not os.path.isdir(submit_dir):
    print("%s doesn't exist" % submit_dir)

if os.path.isdir(submit_dir) and os.path.isdir(truth_dir):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)

    output_filename = os.path.join(output_dir, 'scores.txt')
    output_file = open(output_filename, 'w')

    truth_file = os.path.join(truth_dir, "eval.json")
    with open(truth_file) as f:
        truth = json.load(f)

    submission_answer_file = os.path.join(submit_dir, "output.json")
    with open(submission_answer_file) as f:
        submission = json.load(f)
    SRCC, PLCC, acc = calculate_score(truth, submission)
    output_file.write("SRCC: %.4f\n" % SRCC)
    output_file.write("PLCC: %.4f\n" % PLCC)
    output_file.write("ACC: %.4f\n" % acc)
    final_score = SRCC * 0.25 + PLCC * 0.25 + acc * 0.5
    output_file.write("Final_Score: %.4f\n" % final_score)

    extra_info = open(os.path.join(submit_dir, "readme.txt"), "r")
    output_file.write(extra_info.read())
    extra_info.close()
    output_file.close()
