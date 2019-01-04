# Research

**Owner**: [Purshottam Shivraj](https://github.com/pshivraj)

Current Research work has been around exploring and setting up validation setup for clomask using pre-defined validation images using [matterport](https://github.com/matterport/Mask_RCNN) implimentation. 

Current validation setup is measured against mAP which is defined as average of the maximum precisions at different recall values and is benchmarked at **0.5676** based on the validation process explored in the [clomask_notebook](https://github.com/havanagrawal/clomask/blob/validation_setup/research/clomask_notebook.ipynb).

## Current limitation of model

  ### Matterport(default config)
   * Slant bottles are not detected.
   * Some bottle images having connected lables between them are merged as one causing single mask for two different bottles, throwing off mAP.
