import matplotlib.pyplot as plt
import numpy as np
from sklearn import metrics
from numpy import trapz
from incremental_explainer.utils.common import calculate_intersection_over_union

def compute_insertion_old(model, saliency_map, image, class_index, divisions=100):

        masks = np.empty([saliency_map.shape[0], saliency_map.shape[1], 3])
        conf_insertion_list = []
        divisions_list_in = []
        minimum = np.min(saliency_map) - np.abs(
            (np.min(saliency_map) - np.max(saliency_map)) * 0.2
        )
        maximum = np.max(saliency_map) + np.abs(
            (np.min(saliency_map) - np.max(saliency_map)) * 0.1
        )
        for sub_index in range(0, divisions):
            masks[:, :, :] = False
            threshold = maximum + (sub_index / divisions) * (minimum - maximum)
            pixels = np.where(saliency_map >= threshold)
            masks[pixels[0], pixels[1], :] = True
            divisions_list_in.append(
                len(pixels[0]) / (saliency_map.shape[0] * saliency_map.shape[1])
            )
            min_expl = np.where(masks, image, 0)
            detection = model(min_expl, classes=class_index, verbose=False)
            conf = (
                detection[0].boxes.conf[0]
                if (len(detection[0].boxes.conf) > 0)
                else detection[0].boxes.conf
            )
            conf_insertion_list.append(conf)
        conf_insertion_list = [
            np.sum(conf.numpy()) if conf.numpy().size > 0 else 0
            for conf in conf_insertion_list
        ]
    
        return trapz(conf_insertion_list, divisions_list_in)
    
def compute_insertion(model, saliency_map, image, class_index, bounding_box, divisions=100, verbose = False):
        import matplotlib as mpl
        mpl.rcParams["savefig.pad_inches"] = 0
        masks = np.empty([saliency_map.shape[0], saliency_map.shape[1], 3])
        conf_insertion_list = []
        divisions_list_in = []
        minimum = np.min(saliency_map) - np.abs(
            (np.min(saliency_map) - np.max(saliency_map)) * 0.2
        )
        maximum = np.max(saliency_map) + np.abs(
            (np.min(saliency_map) - np.max(saliency_map)) * 0.1
        )
        im_size = saliency_map.shape[0] * saliency_map.shape[1] * 3
        for sub_index in range(0, divisions):
            masks[:, :, :] = False
            threshold = maximum + (sub_index / divisions) * (minimum - maximum)
            pixels = np.where(saliency_map >= threshold)
            masks[pixels[0], pixels[1], :] = True
            div = len(pixels[0]) / (im_size)
            divisions_list_in.append(
                div
            )
            min_expl = np.where(masks, image, 0)
            detection = model(min_expl, classes=class_index, verbose=False)
            
            arrays = list(zip(np.array(detection[0].boxes.cls), np.array(detection[0].boxes.conf), np.array(detection[0].boxes.xyxy)))

            arrays = [el for el in arrays if el[0] == class_index]

            if len(arrays) > 0:
                max_confidence = max([el[1]* calculate_intersection_over_union(bounding_box, el[2]) for el in arrays])
            else:
                max_confidence = 0

            conf_insertion_list.append(max_confidence)

        auc = trapz(conf_insertion_list, divisions_list_in)
        
        if verbose:
            plt.plot(divisions_list_in, conf_insertion_list)
            plt.title(f'Insertion curve - AUC = {auc}')
    
        return auc