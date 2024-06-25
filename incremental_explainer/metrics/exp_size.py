import matplotlib.pyplot as plt
import numpy as np
from sklearn import metrics
from numpy import trapz
from incremental_explainer.utils.common import calculate_intersection_over_union
import torchvision.transforms as transforms
from vision_explanation_methods.explanations import common as od_common

    
def compute_explanation_size(model: od_common.GeneralObjectDetectionModelWrapper, saliency_map, image, class_index, bounding_box, divisions=100, verbose = False):
        import matplotlib as mpl
        mpl.rcParams["savefig.pad_inches"] = 0
        masks = np.empty([saliency_map.shape[0], saliency_map.shape[1], 3])

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

            if (max_confidence > 0.5):
                if verbose:
                    plt.title(f'Size percentage {div}')
                    plt.imshow(min_expl)
                    plt.show()
                return div

        return -1