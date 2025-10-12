# Copyright CNRS 2024

# simon.chamaille@cefe.cnrs.fr; vincent.miele@univ-lyon1.fr

# This software is a computer program whose purpose is to identify
# animal species in camera trap images.

#This software is governed by the CeCILL  license under French law and
# abiding by the rules of distribution of free software.  You can  use, 
# modify and/ or redistribute the software under the terms of the CeCILL
# license as circulated by CEA, CNRS and INRIA at the following URL
# "http://www.cecill.info". 

# As a counterpart to the access to the source code and  rights to copy,
# modify and redistribute granted by the license, users are provided only
# with a limited warranty  and the software's author,  the holder of the
# economic rights,  and the successive licensors  have only  limited
# liability. 

# In this respect, the user's attention is drawn to the risks associated
# with loading,  using,  modifying and/or developing or reproducing the
# software by the user in light of its specific status of free software,
# that may mean  that it is complicated to manipulate,  and  that  also
# therefore means  that it is reserved for developers  and  experienced
# professionals having in-depth computer knowledge. Users are therefore
# encouraged to load and test the software's suitability as regards their
# requirements in conditions enabling the security of their systems and/or 
# data to be ensured and,  more generally, to use and operate it in the 
# same conditions as regards security. 

# The fact that you are presently reading this means that you have had
# knowledge of the CeCILL license and that you accept its terms.

import logging
import sys
import os
import numpy as np
import timm
import torch
from torch import tensor
import torch.nn as nn
from torchvision.transforms import InterpolationMode, transforms

CROP_SIZE = 182
BACKBONE = "vit_large_patch14_dinov2.lvd142m"
DFPATH = os.path.abspath(os.path.dirname(__file__))
DFVIT_WEIGHTS = os.path.join(DFPATH, 'weights', 'deepfaune-vit_large_patch14_dinov2.lvd142m.v3.pt')

txt_animalclasses = {
    'fr': ['bison', 'blaireau', 'bouquetin', 'castor', 'cerf', 'chamois', 'chat', 'chevre', 'chevreuil', 'chien', 'daim', 'ecureuil', 'elan', 'equide', 'genette', 'glouton', 'herisson', 'lagomorphe', 'loup', 'loutre', 'lynx', 'marmotte', 'micromammifere', 'mouflon', 'mouton', 'mustelide', 'oiseau', 'ours', 'ragondin', 'raton laveur', 'renard', 'renne', 'sanglier', 'vache'],
    'en': ['bison', 'badger', 'ibex', 'beaver', 'red deer', 'chamois', 'cat', 'goat', 'roe deer', 'dog', 'fallow deer', 'squirrel', 'moose', 'equid', 'genet', 'wolverine', 'hedgehog', 'lagomorph', 'wolf', 'otter', 'lynx', 'marmot', 'micromammal', 'mouflon', 'sheep', 'mustelid', 'bird', 'bear', 'nutria', 'raccoon', 'fox', 'reindeer', 'wild boar', 'cow'],
    'it': ['bisonte', 'tasso', 'stambecco', 'castoro', 'cervo', 'camoscio', 'gatto', 'capra', 'capriolo', 'cane', 'daino', 'scoiattolo', 'alce', 'equide', 'genetta', 'ghiottone', 'riccio', 'lagomorfo', 'lupo', 'lontra', 'lince', 'marmotta', 'micromammifero', 'muflone', 'pecora', 'mustelide', 'uccello', 'orso', 'nutria', 'procione', 'volpe', 'renna', 'cinghiale', 'mucca'],
    'de': ['Bison', 'Dachs', 'Steinbock', 'Biber', 'Rothirsch', 'Gämse', 'Katze', 'Ziege', 'Rehwild', 'Hund', 'Damwild', 'Eichhörnchen', 'Elch', 'Equide', 'Ginsterkatze', 'Vielfraß', 'Igel', 'Lagomorpha', 'Wolf', 'Otter', 'Luchs', 'Murmeltier', 'Kleinsäuger', 'Mufflon', 'Schaf', 'Marder', 'Vogel', 'Bär', 'Nutria', 'Waschbär', 'Fuchs', 'Rentier', 'Wildschwein', 'Kuh'],
    'es': ['bisonte', 'tejón', 'cabra montés', 'castor', 'ciervo rojo', 'rebeco', 'gato', 'cabra', 'corzo', 'perro', 'gamo', 'ardilla', 'alce', 'équido', 'gineta', 'glotón', 'erizo', 'lagomorfo', 'lobo', 'nutria', 'lince', 'marmota', 'micromamífero', 'muflón', 'oveja', 'mustélido', 'ave', 'oso', 'coipú', 'mapache', 'zorro', 'reno', 'jabalí', 'vaca'],
}

####################################################################################
### CLASSIFIER
####################################################################################
class Classifier:

    def __init__(self, device=None):
        self.model = Model(device)
        self.model.loadWeights(DFVIT_WEIGHTS)
        self.transforms = transforms.Compose([
            transforms.Resize(size=(CROP_SIZE, CROP_SIZE), interpolation=InterpolationMode.BICUBIC, max_size=None, antialias=None),
            transforms.ToTensor(),
            transforms.Normalize(mean=tensor([0.4850, 0.4560, 0.4060]), std=tensor([0.2290, 0.2240, 0.2250]))])

    def predictOnBatch(self, batchtensor, withsoftmax=True):
        return self.model.predict(batchtensor, withsoftmax)

    # croppedimage loaded by PIL
    def preprocessImage(self, croppedimage):
        preprocessimage = self.transforms(croppedimage)
        return preprocessimage.unsqueeze(dim=0)


####################################################################################
### MODEL
####################################################################################

class Model(nn.Module):
    def __init__(self, device=None):
        """
        Constructor of model classifier
        """
        super().__init__()
        self.base_model = timm.create_model(BACKBONE, pretrained=False, num_classes=len(txt_animalclasses['fr']),
                                            dynamic_img_size=True)
        logging.info(f"Using {BACKBONE} for classification")
        self.backbone = BACKBONE
        self.nbclasses = len(txt_animalclasses['fr'])
        self.device = device

    def forward(self, input):
        x = self.base_model(input)
        return x

    def predict(self, data, withsoftmax=True):
        """
        Predict on test DataLoader
        :param test_loader: test dataloader: torch.utils.data.DataLoader
        :return: numpy array of predictions without soft max
        """
        self.eval()
        self.to(self.device)
        total_output = []
        with torch.no_grad():
            x = data.to(self.device)
            if withsoftmax:
                output = self.forward(x).softmax(dim=1)
            else:
                output = self.forward(x)
            total_output += output.tolist()

        return np.array(total_output)

    def loadWeights(self, path):
        """
        :param path: path of .pt save of model
        """
        if path[-3:] != ".pt":
            path += ".pt"
        try:
            params = torch.load(path, map_location=self.device)
            args = params['args']
            if self.nbclasses != args['num_classes']:
                raise Exception("You load a model ({}) that does not have the same number of class"
                                "({})".format(args['num_classes'], self.nbclasses))
            self.backbone = args['backbone']
            self.nbclasses = args['num_classes']
            self.load_state_dict(params['state_dict'])
        except Exception as e:
            print("Can't load checkpoint model because :\n\n " + str(e), file=sys.stderr)
            raise e
