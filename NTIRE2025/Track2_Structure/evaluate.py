import sys       
import os
import numpy as np
import pickle
import cv2
from scipy.stats import spearmanr
import scipy.stats
from scipy.optimize import curve_fit

def logistic_func(X, bayta1, bayta2, bayta3, bayta4):
    # 4-parameter logistic function
    logisticPart = 1 + np.exp(np.negative(np.divide(X - bayta3, np.abs(bayta4))))
    # breakpoint()
    yhat = bayta2 + np.divide(bayta1 - bayta2, logisticPart)
    return yhat

def get_plcc_srcc(y_pred, y):
    # for (output_scores, gt_scores) in zip(output_scores_list, gt_scores_list):
    y_pred = np.array(y_pred)
    y = np.array(y)
    # Calculate PLCC (Pearson Linear Correlation Coefficient)
    beta_init = [np.max(y), np.min(y), np.mean(y_pred), np.std(y_pred)]
    popt, _ = curve_fit(logistic_func, y_pred, y, p0=beta_init, maxfev=int(1e8))
    y_pred_logistic = logistic_func(y_pred, *popt)
    plcc = scipy.stats.pearsonr(y, y_pred_logistic)[0]

    # Calculate SRCC (Spearman Rank Correlation Coefficient)
    srcc, _ = spearmanr(y, y_pred)
    return plcc, srcc

def find_connected_components(mask, area_threshold=0):
    mask = mask.astype(np.uint8)
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    regions = []

    for contour in contours:
        area = cv2.contourArea(contour)
        if area >= area_threshold:
            x, y, w, h = cv2.boundingRect(contour)
            regions.append((x, y, w, h, contour))  

    return regions

def calculate_pixel_iou(contour1, contour2, mask1, mask2):

    region_mask1 = np.zeros(mask1.shape, dtype=np.uint8)
    cv2.drawContours(region_mask1, [contour1], -1, 1, thickness=cv2.FILLED)

    region_mask2 = np.zeros(mask2.shape, dtype=np.uint8)
    cv2.drawContours(region_mask2, [contour2], -1, 1, thickness=cv2.FILLED)

    intersection = np.logical_and(region_mask1, region_mask2).sum()
    union = np.logical_or(region_mask1, region_mask2).sum()
    
    if union == 0:
        return 0.0  
    iou = intersection / union
    return iou

def calculate_miou(prediction, ground_truth, num_classes):
    intersection = np.zeros(num_classes)
    union = np.zeros(num_classes)

    for i in range(num_classes):
        pred_i = (prediction == i)
        gt_i = (ground_truth == i)

        intersection[i] = np.sum(np.logical_and(pred_i, gt_i))
        union[i] = np.sum(np.logical_or(pred_i, gt_i))

    iou = (intersection + 1e-4) / (union + 1e-4)
    return iou



def pixel_pr(pred_regions, gt_regions, pred_mask, gt_mask, iou_thres):
    gt_hits = np.array([0] * len(gt_regions))
    pred_hits = np.array([0] * len(pred_regions))
    for pred_idx, pred_region in enumerate(pred_regions):
        for gt_idx, gt_region in enumerate(gt_regions):
            _,_,_,_,counters1 = pred_region
            _,_,_,_,counters2 = gt_region
            iou = calculate_pixel_iou(counters1, counters2, pred_mask, gt_mask)
            if iou > iou_thres:
                gt_hits[gt_idx] = 1
                pred_hits[pred_idx] = 1
                break
    
    for gt_idx, gt_region in enumerate(gt_regions):
        if gt_hits[gt_idx] == 1:
            continue
        for pred_idx, pred_region in enumerate(pred_regions):
            _,_,_,_,counters1 = pred_region
            _,_,_,_,counters2 = gt_region
            iou = calculate_pixel_iou(counters1, counters2, pred_mask, gt_mask)
            if iou > iou_thres:
                gt_hits[gt_idx] = 1
                pred_hits[pred_idx] = 1
                break

    return gt_hits, pred_hits


def get_pixel_hits(pred_map, gt_map,iou_thres, pre_area_thres=0.,gt_area_thres=0.):
    pred_contours = find_connected_components(pred_map)
    gt_contours = find_connected_components(gt_map)
    pred_contoures = [(x1,y1,x2,y2,contour) for x1,y1,x2,y2,contour in pred_contours if cv2.contourArea(contour)>pre_area_thres]
    gt_contoures = [(x1,y1,x2,y2,contour) for x1,y1,x2,y2,contour in gt_contours if cv2.contourArea(contour)>gt_area_thres]
    gt_hits, pred_his = pixel_pr(pred_contoures, gt_contoures, pred_map, gt_map,iou_thres)
    return gt_hits, pred_his, gt_contoures, pred_contoures


def metric_cal_vis(pred_dir, gt_dir,
    area_thres_ratio = 0.0001, bbox_iou_thres = 0.1, area_weight=0.7, score_weight=0.3):

    with open(pred_dir, 'rb') as f:
        pred_data = pickle.load(f)

    with open(gt_dir, 'rb') as f:
        gt_data = pickle.load(f)


    alpha = 0.3
    gt_bbox_nums = 0
    pred_bbox_nums = 0
    miss_bbox_nums = 0
    hit_bbox_nums = 0
    gious = 0.
    num = len(gt_data)
    pred_scores, gt_scores = [],[]
    
    for image_name in gt_data.keys():
        # breakpoint()
        pred_map, pred_score = pred_data[image_name]['pred_area'], pred_data[image_name]['score']
        gt_map, gt_score = gt_data[image_name]['pred_area'], gt_data[image_name]['score']

        pred_scores.append(pred_score)
        gt_scores.append(gt_score)

        pred_map = cv2.resize(pred_map, (512,512))
        pred_map[pred_map > 0] = 1

        
        img_h, img_w = pred_map.shape
        area_thres = img_h * img_w * area_thres_ratio

        gt_hits, pred_hits, gt_bboxes,pred_bboxes = get_pixel_hits(pred_map, gt_map, bbox_iou_thres, area_thres, 150)
        mask_ious = calculate_miou(pred_map, gt_map, 2)
        gious +=mask_ious[1]

        gt_bbox_nums+= len(gt_bboxes)
        assert len(gt_bboxes) == len(gt_hits),f'gt_bboxes and gt_hits not match:{len(gt_bboxes)},{len(gt_hits)}'
        pred_bbox_nums+= len(pred_bboxes)
        miss_bbox_nums+= np.sum(gt_hits==0)
        hit_bbox_nums+= np.sum(pred_hits==1)
    # breakpoint()
    precision = hit_bbox_nums/pred_bbox_nums
    recall = 1. - miss_bbox_nums/gt_bbox_nums
    f1_score = 2 * precision * recall / (precision + recall + 1e-10)
    giou = gious/num
    plcc, srcc = get_plcc_srcc(pred_scores, gt_scores)
    final_score = f1_score * area_weight + (plcc+srcc)* score_weight/2

    results = {
        'precision': precision,
        'recall': recall,
        'f1_score': f1_score,
        'giou': giou,
        'plcc': plcc,
        'srcc': srcc,
        'final_score': final_score,
    }
    return results



if __name__ == "__main__":

    # 面积阈值，最后是取 图像大小 x area_thres_ratio 作为面积阈值
    area_thres_ratio = 0.0006
    # 区域交集的iou阈值
    bbox_iou_thres = 0.1
    input_dir = sys.argv[1]
    output_dir = sys.argv[2]

    submit_dir = os.path.join(input_dir, 'res')
    truth_dir = os.path.join(input_dir, 'ref')

    ## 传入的文件路径
    gt_file = os.path.join(truth_dir, "gt.pkl")
    pred_file = os.path.join(submit_dir, "output.pkl")

    result = metric_cal_vis(pred_file, gt_file, area_thres_ratio, bbox_iou_thres)

    output_filename = os.path.join(output_dir, 'scores.txt')
    output_file = open(output_filename, 'w')
    output_file.write("Final_Score: %.4f\n" % result['final_score'])
    output_file.write("SRCC: %.4f\n" % result['srcc'])
    output_file.write("PLCC: %.4f\n" % result['plcc'])
    output_file.write("Precision: %.4f\n" % result['precision'])
    output_file.write("Recall: %.4f\n" % result['recall'])
    output_file.write("F1_Score: %.4f\n" % result['f1_score'])
    output_file.write("GIoU: %.4f\n" % result['giou'])

    extra_info = open(os.path.join(submit_dir, "readme.txt"), "r")
    output_file.write(extra_info.read())
    extra_info.close()
    output_file.close()
