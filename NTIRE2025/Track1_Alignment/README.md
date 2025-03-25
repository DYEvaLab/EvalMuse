## Evaluation Data and Script for NTIRE 2025 Text to Image Generation Model Quality Assessment - Track 1 Image-Text Alignment 

### File Directory
```
.
├── evaluate.py          # Evaluation script
├── ref
│   └── eval.json        # Ground truth file
├── res
│   ├── output.json      # Model output file
│   └── readme.txt       # Description file for the model output
└── output
    └── scores.txt       # Evaluation results
```

### Data Preparation
- The development phase annotation data ```eval.json``` can be found at [link](https://drive.google.com/file/d/1aeKUM_A0pdWZ9wcVymHAnOuLUsPFRDfS/view?usp=sharing). Please download it and place it in the ```./ref```.
- Prepare your model output ```output.json``` and a README file ```readme.txt```, then place them in the ```./res```.

### Evaluation
To run the evaluation script, execute the following command:
``` 
python3 evaluate.py ./ ./output
```
The script will generate the evaluation results and save them in the ```./output```.

