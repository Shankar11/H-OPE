#!/usr/bin/env python
# coding: utf-8

import os,sys
sys.path.insert(0,"..")
from glob import glob
import matplotlib.pyplot as plt
import numpy as np
import argparse
import skimage, skimage.io
import pprint


import torch
import torch.nn.functional as F
import torchvision, torchvision.transforms

import torchxrayvision as xrv

parser = argparse.ArgumentParser()
parser.add_argument('-f', type=str, default="", help='')
#parser.add_argument('img_path', type=str)
parser.add_argument('-weights', type=str,default="densenet121-res224-all")
parser.add_argument('-feats', default=False, help='', action='store_true')
parser.add_argument('-cuda', default=False, help='', action='store_true')
parser.add_argument('-resize', default=False, help='', action='store_true')

cfg = parser.parse_args()

def classifyxray(img_path):

	img = skimage.io.imread(img_path)
	img = xrv.datasets.normalize(img, 255)  

	# Check that images are 2D arrays
	if len(img.shape) > 2:
		img = img[:, :, 0]
	if len(img.shape) < 2:
		print("error, dimension lower than 2 for image")

	# Add color channel
	img = img[None, :, :]


	# the models will resize the input to the correct size so this is optional.
	if cfg.resize:
		transform = torchvision.transforms.Compose([xrv.datasets.XRayCenterCrop(),
													xrv.datasets.XRayResizer(224)])
	else:
		transform = torchvision.transforms.Compose([xrv.datasets.XRayCenterCrop()])

	img = transform(img)


	model = xrv.models.get_model(cfg.weights)

	output = {}
	with torch.no_grad():
		img = torch.from_numpy(img).unsqueeze(0)
		if cfg.cuda:
			img = img.cuda()
			model = model.cuda()
			
		if cfg.feats:
			feats = model.features(img)
			feats = F.relu(feats, inplace=True)
			feats = F.adaptive_avg_pool2d(feats, (1, 1))
			output["feats"] = list(feats.cpu().detach().numpy().reshape(-1))

		preds = model(img).cpu()
		output["preds"] = dict(zip(xrv.datasets.default_pathologies,preds[0].detach().numpy()))
		
	if cfg.feats:
		print('1')
		return output
	else:
		pprint.pprint('2')
		return output
    
   

def segmentxray(img_path):
	model = xrv.baseline_models.chestx_det.PSPNet()

	img = skimage.io.imread(img_path)
	img = xrv.datasets.normalize(img, 255) # convert 8-bit image to [-1024, 1024] range
	img = img.mean(2)[None, ...] # Make single color channel

	transform = torchvision.transforms.Compose([xrv.datasets.XRayCenterCrop(),xrv.datasets.XRayResizer(512)])

	img = transform(img)
	img = torch.from_numpy(img)
	with torch.no_grad():
		pred = model(img)

	plt.figure(figsize = (26,5))
	plt.subplot(1, len(model.targets) + 1, 1)
	plt.imshow(img[0], cmap='gray')
	for i in range(len(model.targets)):
		plt.subplot(1, len(model.targets) + 1, i+2)
		plt.imshow(pred[0, i])
		plt.title(model.targets[i])
		plt.axis('off')
	plt.tight_layout()
	plt.savefig('./static/uploads/segmentxray.jpeg')
	return 'segmentxray.jpeg'