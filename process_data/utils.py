import os
import json
import pickle
import re
from spacy.lang.en import English


def listdir_fullpath(d):
    return [os.path.join(d, f) for f in os.listdir(d)]


def get_pickle(file_path):
    with open(file_path, 'rb') as fp:
        x = pickle.load(fp)
    return x


def write_pickle(pickle_obj, file_path):
    with open(file_path, 'wb') as fp:
        pickle.dump(pickle_obj, fp)


def read_file(fname, each_line=None, print_patience=1000):
    lines = []
    with open(fname, 'r', encoding='utf-8') as f:
        for i, line in enumerate(f):
            line = line.strip()
            if each_line == 'json':
                lines.append(json.loads(line))
            elif not each_line:
                lines.append(line)
            else:
                raise NotImplementedError("supported options for each_line: json/None, found {}".format(each_line))

            if i > 0 and i % print_patience == 0:
                print("processed {} lines".format(i), end='\r')
    return lines


def tokenize_file(in_filepath, out_filepath, remove_existing_tags=False):
    sen_start = " <t> "
    sen_end = " </t> "
    nlp = English()
    sentencizer = nlp.create_pipe("sentencizer")
    nlp.add_pipe(sentencizer)
    with open(in_filepath, 'r') as ifp, open(out_filepath, 'w') as ofp:
        for line in ifp:
            line = line.strip()
            if remove_existing_tags:
                line = line.replace("<t>", "").replace("</t>", "")
            doc = nlp(line)
            tokenized_line = sen_start + (sen_end + sen_start).join([s.text for s in doc.sents]) + sen_end
            tokenized_line  = tokenized_line + "\n"
            ofp.write(tokenized_line)


def get_sent_tokenizer(tokenizer='spacy'):
    if tokenizer == 'spacy':
        nlp = English()
        sentencizer = nlp.create_pipe("sentencizer")
        nlp.add_pipe(sentencizer)
        return nlp
    else:
        raise NotImplementedError("supported tokenizers spacy, received {}".format(tokenizer))


def get_word_tokenizer(tokenizer='spacy'):
    if tokenizer == 'spacy':
        nlp = English()
        tokenizer = nlp.Defaults.create_tokenizer(nlp)
        return tokenizer
    else:
        raise NotImplementedError("supported tokenizers spacy, received {}".format(tokenizer))


def sent_tokenize(text: str, tokenizer_fn: any = None, tokenizer: str = 'spacy') -> list:
    """
    :param text: text to tokenize
    :param tokenizer_fn: tokenizer will be called as tokenizer_fn(text)
    :param tokenizer: which type of tokenizer - spacy supported for now.
    :return: list of sentence tokenized sentences
    """
    if tokenizer == 'spacy':
        doc = tokenizer_fn(text)
        return [sent.text for sent in doc.sents]
    else:
        raise NotImplementedError("supported tokenizers spacy, received {}".format(tokenizer))


def get_chunks(long_list, num_chunks):
    chunk_size = len(long_list) // num_chunks
    return [long_list[i: i + chunk_size] for i in range(0, len(long_list) - 1, chunk_size)]


def sent_tokenize_by_tags(text: str) -> list:
    # pdb.set_trace()
    text = text.strip()
    if len(text) == 0:
        return []
    b = text.find('<t>')
    assert b != -1, "expect at least one sentence when text is not empty"
    # prev_e = -3
    l = []
    while b!=-1:
        assert len(text[:b].strip()) == 0, f"expect only blanks outside of in-between tags, " \
                                                   f"encountered {text[:b].strip()}" \
                                                   f"where b:{b}"
        text = text[b+3:]
        e = text.find('</t>')
        sen = text[:e].strip()
        l.append(sen)
        text = text[e+4:]
        b = text.find('<t>')
        # prev_e = e
    assert len(text[e+4:].strip()) == 0, f"expect only blanks after last tag, " \
                                              f"encountered {text[e+4:].strip()}"
    return l


def sent_list_to_tagged_str(l):
    sen_start = " <t> "
    sen_end = " </t> "
    tagged_str = sen_start + (sen_end + sen_start).join(l) + sen_end
    return tagged_str


def apply_function_to_all_items_in_dir(function, in_dir_path, out_dir_path,
                                       args_list=[], kwargs_dict={},
                                       onlyFile=False, onlyDir=False, quiet=False):
    assert not (onlyFile and onlyDir), "at most one of onlyFile or onlyDir should be true"
    assert os.path.isdir(in_dir_path)
    assert os.path.isdir(out_dir_path)
    for item in os.listdir(in_dir_path):
        in_item_path = os.path.join(in_dir_path, item)
        out_item_path = os.path.join(out_dir_path, item)
        if onlyFile and not os.path.isfile(in_item_path):
            continue
        elif onlyDir and not os.path.isdir(in_item_path):
            continue
        if not quiet:
            print(f"applying function to {in_item_path}")
        function(in_path=in_item_path,
                 out_path=out_item_path,
                 *args_list, **kwargs_dict)


def retain_first_n_sent(in_filepath, out_filepath, n):
    nlp = English()
    sentencizer = nlp.create_pipe("sentencizer")
    nlp.add_pipe(sentencizer)
    with open(in_filepath, 'r') as ifp, open(out_filepath, 'w') as ofp:
        for idx,line in enumerate(ifp):
            line = line.strip()
            doc = nlp(line)
            out = " ".join([s.text for s in doc.sents][:n])
            ofp.write(out + "\n")
            if (idx%1000)==0:
                print(f"{idx}", end="\r")


def get_sents_from_tags(text, sent_start_tag, sent_end_tag):
    sents = re.findall(r'%s (.+?) %s' % (sent_start_tag, sent_end_tag), text)
    sents = [sent for sent in sents if len(sent) > 0]  # remove empty sents
    return sents
