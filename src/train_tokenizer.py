from pathlib import Path
from loguru import logger
from transformers import AutoTokenizer
from tqdm import tqdm

def get_combine_text_file(input_dirs, output_file='./corpus.txt'):
    if not isinstance(input_dirs, list):
        input_dirs = [input_dirs]
    output_file = Path(output_file)

    text_list = []
    for idx, root in enumerate(input_dirs):
        for filename in tqdm(list(Path(root).glob('**/*.phe')), desc=f"Read text file {idx+1}/{len(input_dirs)}"):
            text = filename.read_text()
            text_list.append(text)
    
    output_file.write_text('\n'.join(text_list))
    logger.info(f"All text file combine to {output_file}, total {len(text_list)} lines.") 
    return output_file

def get_trainnig_corpus(text_file):
    text_file = Path(text_file)
    text_list = text_file.read_text().split('\n')
    for start_idx in range(0, len(text_list), 1000):
        samples = text_list[start_idx : start_idx + 1000]
        yield samples

def huggingface_train_new_tokenizer(ori_tokenzier, output_dir, data_dir):
    old_tokenizer = AutoTokenizer.from_pretrained(ori_tokenzier)
    corpus_file = get_combine_text_file(data_dir)
    corpus = get_trainnig_corpus(corpus_file)

    logger.info("Start training new tokenizer.")
    new_tokenizer = old_tokenizer.train_new_from_iterator(corpus, vocab_size=32000)
    new_tokenizer.save_pretrained(output_dir)
    logger.info(f"New tokenizer is save at {output_dir}.")

if __name__ == '__main__':
    ori_tokenzier = '/home/zhongjiafeng/repo/fish-speech/checkpoints/fish-speech-1.2-sft'
    output_dir = '/home/zhongjiafeng/repo/fish-speech/checkpoints/ar_tokenizer'
    data_dir = ["/data/zhongjiafeng/Arabic/AFS"]
    huggingface_train_new_tokenizer(ori_tokenzier, output_dir, data_dir)





