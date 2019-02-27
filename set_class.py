import json
import os
import tossi

def assignment(sentences, c, p, o) :
    new_sentences = []
    for sentence in sentences:
        phrases = sentence.strip().split()
        length = len(phrases)
        for i in range(length):
            phrase = phrases[i]
            #print(phrase)
            words = phrase.split('(P)')
            new_phrase = ''
            #print(words)
            if (phrase.find('(P)') == 0) :
                for word in words :
                    if (word == '') : continue
                    new_phrase = new_phrase + tossi.postfix(p, word)
                phrases[i] = new_phrase
            elif (phrase.find('(P)') > 0) :    
                new_phrase = words[0]
                for word in words[1:] :
                    if (word == '') : continue
                    new_phrase = new_phrase + tossi.postfix(p, word)
                phrases[i] = new_phrase
        sentence = ' '.join(phrases)
        for old, new in [('(S)', '['+c+']'), ('(O)', o)] :
            sentence = sentence.replace(old, new)    
        new_sentences.append(sentence)
    return new_sentences
        


if __name__ == "__main__":
    qa_form = json.load(open('_merged.json', 'r', encoding='utf8'))
    f = open('triple_type.json', 'r', encoding='utf-8')
    triple_type = json.load(f)

    qa_f = open('qa_format.json', 'w', encoding='utf-8')
    qa_format = dict()
    for s_class, v1 in qa_form.items() :
        qa_format[s_class] = dict()
        print(s_class, v1.keys())
        for predicate, v2 in v1.items() :
            o_class = str(triple_type[s_class][predicate]).replace("'", '')
            questions = v2['questions']
            answers = v2['answers']
            new_questions = assignment(questions, s_class, predicate, o_class)
            new_answers = assignment(answers, s_class, predicate, o_class)
            qa_format[s_class][predicate] = dict()
            qa_format[s_class][predicate]['questions'] = new_questions
            qa_format[s_class][predicate]['answers'] = new_answers
            #print(new_answers)
    json.dump(qa_format, qa_f, ensure_ascii=False, indent='\t')