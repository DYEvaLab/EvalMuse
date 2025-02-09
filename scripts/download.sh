git lfs install
git clone https://huggingface.co/datasets/DY-Evalab/EvalMuse
cd EvalMuse
cat images.zip.part-* > images.zip
unzip -d ../ images.zip
mv *.json ../dataset
