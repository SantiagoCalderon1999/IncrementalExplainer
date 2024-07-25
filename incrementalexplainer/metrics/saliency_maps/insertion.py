import matplotlib.pyplot as plt
import numpy as np
from sklearn import metrics
from numpy import trapz
from incrementalexplainer.utils.common import calculate_intersection_over_union
import torchvision.transforms as transforms
from incrementalexplainer.dependencies.d_rise.vision_explanation_methods.explanations import common as od_common
from tqdm import tqdm
    
def compute_insertion(model: od_common.GeneralObjectDetectionModelWrapper, saliency_map, image, class_index, bounding_box, divisions=100, verbose = False):
        import matplotlib as mpl
        mpl.rcParams["savefig.pad_inches"] = 0
        masks = np.empty([saliency_map.shape[0], saliency_map.shape[1], 3])
        conf_insertion_list = []
        divisions_list_in = []
        minimum = np.min(saliency_map)
        maximum = np.max(saliency_map)
        thresholds = np.linspace(start=minimum, stop=maximum, num=divisions).tolist()
        thresholds = thresholds[::-1]
        im_size = saliency_map.shape[0] * saliency_map.shape[1] * 3
        for threshold in tqdm(thresholds):
            masks[:, :, :] = False
            pixels = np.where(saliency_map >= threshold)
            masks[pixels[0], pixels[1], :] = True
            div = len(np.where(masks)[0]) / (im_size)
            divisions_list_in.append(
                div
            )
            min_expl = np.where(masks, image, 0)
            transform = transforms.Compose([
                transforms.ToTensor()
            ])
            img_t = transform(min_expl)
            detection = model.predict([img_t])            
            arrays = []
            
            for i, _ in enumerate(detection[0].bounding_boxes.cpu().detach()):
                index = np.argmax(detection[0].class_scores[i].cpu().detach())
                if index == class_index:
                    arrays.append((detection[0].class_scores[i][index].cpu().detach(), detection[0].bounding_boxes[i].cpu().detach()))
            if len(arrays) > 0:
                max_confidence = max([el[0] * calculate_intersection_over_union(bounding_box, el[1]) for el in arrays])
            else:
                max_confidence = 0

            conf_insertion_list.append(max_confidence)

        auc = trapz(conf_insertion_list, divisions_list_in)
        if verbose:
            plt.plot(divisions_list_in, conf_insertion_list)
            plt.title(f'Insertion curve - AUC = {auc}')
            plt.show()
    
        return auc