# 数据处理流程

1.`raw_extract.py` 提取音频文件和文本到数据文件夹，并给音频样本编号
2.`data_check.py` 检查文本中是否包含有非阿拉伯语字符，如果包含，则把该样本丢弃
3.`g2p_transfrom.py` 将文本转换为音素表示，并存储为.phe文件
5.`extract_vq.py` 提取音频文件的语音编码 .npy文件
4.`data_check.py` 检查每个样本是否都包含 .wav .phe .lab文件
7.`build_data.py` 生成proto文件


```
bash ./src/pipline.sh /data/zhongjiafeng/Arabic/raw /data/zhongjiafeng/Arabic/AFS/data-04 1 6
```