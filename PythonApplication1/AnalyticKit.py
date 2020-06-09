import nltk
import Support
import time
import random
import math
import pickle
import FileManager as fm

from langdetect import detect_langs

from nltk.stem.wordnet import WordNetLemmatizer
from nltk.corpus import twitter_samples, stopwords
from nltk.tag import pos_tag
from nltk.tokenize import word_tokenize
from nltk.tokenize import RegexpTokenizer
from nltk.tokenize import TweetTokenizer

from nltk.corpus import stopwords
from nltk import FreqDist, classify, NaiveBayesClassifier
from nltk.twitter import json2csv

from nltk.stem.snowball import SnowballStemmer

from pymystem3 import Mystem
from string import punctuation

class Analytic():
    mystem = Mystem()


    def Downloads(self):
        nltk.download("stopwords")
        nltk.download("punkt")
        nltk.download('wordnet')
        nltk.download('averaged_perceptron_tagger')


    def Tokenize(self, text):
        if type(text) is not list:
            text = [text] 
        
        tokenizer = TweetTokenizer(preserve_case=False, strip_handles=True, reduce_len=True)
        tokens=[]
        for str in text:
            tokens.append(tokenizer.tokenize(str))
        return tokens


    def __lemmatize_russian_text(self,text):
        russian_stopwords = stopwords.words("russian")

        tokens = self.mystem.lemmatize(text.lower())
        tokens = [token for token in tokens if token not in russian_stopwords\
                  and token != " " \
                  and token.strip() not in punctuation]
        return tokens


    def __lemmatize_english_text(self,text):
        tokens = self.Tokenize(text)

        lemmatizer = WordNetLemmatizer()
        lemmatized_sentence = []

        english_stopwords = stopwords.words("english")

        for word, tag in pos_tag(tokens[0]):
            if tag.startswith('NN'):
                pos = 'n'
            elif tag.startswith('VB'):
                pos = 'v'
            else:
                pos = 'a'
            lemma = lemmatizer.lemmatize(word, pos)
            lemmatized_sentence.append(lemma)
            lemmatized_sentence = [token for token in lemmatized_sentence if token not in english_stopwords\
                  and token != " " \
                  and token.strip() not in punctuation]
        return lemmatized_sentence


    def TagWords(self, tokens, lang):
        return pos_tag(tokens,lang = lang)

    def Stemming(self, text):
        if type(text) is not list:
            text = [text] 

        start_time = time.time()
        count = len(text)
        print("Стемминг текстового корпуса из {0} строк. Начато {1}".format(count, Support.ConvertStampToTime(start_time)))
        
        i=0
        result=[]
        for str in text:
            i+=1
            tokens = self.Tokenize(str)
            detrmine_lang = detect_langs(str)
            language="english"
            if detrmine_lang[0].lang =='ru':
                language="russian"
            elif detrmine_lang[0].lang =='en':
                language="english"  
                
            stemmer = SnowballStemmer(language, ignore_stopwords=True)
            my_stopwords = stopwords.words(language)

            stems=[]
            for token in tokens[0]:
                stems.append(stemmer.stem(token))
            stems = [stem for stem in stems if stem not in my_stopwords\
                and stem != " " \
                and stem.strip() not in punctuation]
            
            result.append(stems)
            now = time.time()
            print("{0}: Обработано {1} из {2} строк".format(Support.ConvertStampToTime(now), i, count))


        now = time.time()
        print('{0}: Стемминг завершен. Выполнено за {1} cек \n'.format(Support.ConvertStampToTime(now), now - start_time))
        return result


    def Lemmatization(self, text):
        if type(text) is not list:
            text = [text] 

        start_time = time.time()
        count = len(text)
        print("Лемматизация текстового корпуса из {0} строк. Начато {1}".format(count, Support.ConvertStampToTime(start_time)))

        i=0
        res=[]
        for str in text:
            i+=1
            language = detect_langs(str)
            if language[0].lang =='ru':
                res.append(self.__lemmatize_russian_text(str))
            elif language[0].lang =='en':
                res.append(self.__lemmatize_english_text(str))      
            else:
                res.append(self.__lemmatize_english_text(str))# заглушка нужна
            
            now = time.time()
            print("{0}: Обработано {1} из {2} строк".format(Support.ConvertStampToTime(now), i, count))
        
        now = time.time()
        print('{0}: Лемматизация завершена. Выполнено за {1} cек \n'.format(Support.ConvertStampToTime(now), now - start_time))
        return res

    def CalculateWordsFrequency(self, tokens):
        words = self.GetAllWords(tokens)
        freq_dist = FreqDist(words)
        return freq_dist


    def GetAllWords(self, cleaned_tokens_list):
        for tokens in cleaned_tokens_list:
           for token in tokens:
               yield token

    def Classifier(self, model):
        classifier = nltk.NaiveBayesClassifier
        classifier = model
        return classifier

    def GetDictionaryForModel(self, cleaned_tokens_list):
       for tokens in cleaned_tokens_list:
           yield dict([token, True] for token in tokens)

    def Classify(self, model, text, lemmatized_model = True):
        if type(text) is not list:
            text = [text] 

        model = self.Classifier(model)
        if lemmatized_model:
            tokens = self.Lemmatization(text)
        else:
            tokens = self.Stemming(text)

        dictionary =  self.GetDictionaryForModel(tokens) #dict([token, True] for token in tokens)
        classification = model.classify_many(dictionary)

        result = list(zip(text, classification))
        return result


    def TrainSentimentsPredictionModel(self, positive_tokens, negative_tokens):
        start_time = time.time()
        print("Обучение модели распознавания эмоций сообщения. Начато {0}".format(Support.ConvertStampToTime(start_time)))
        
        model_tokens_pos = self.GetDictionaryForModel(positive_tokens)
        model_tokens_neg = self.GetDictionaryForModel(negative_tokens)

        positive_dataset = [(text_dict1, "Positive")
                        for text_dict1 in model_tokens_pos]

        negative_dataset = [(text_dict2, "Negative")
                            for text_dict2 in model_tokens_neg]

        dataset = positive_dataset + negative_dataset

        random.shuffle(dataset)

        size = math.ceil(len(dataset)*0.8)
        train_data = dataset[:size]
        test_data = dataset[size:]
        now = time.time()
        print("{0}: Данные для обучения модели приведены к необходимому виду".format(Support.ConvertStampToTime(now)))
        print("{0}: Начинается обучение модели. Может занять значительное время".format(Support.ConvertStampToTime(now)))

        classifier = NaiveBayesClassifier.train(train_data)
        now = time.time()

        print("Точность прогноза модели: ", classify.accuracy(classifier, test_data))
        print('Наиболее информативные элементы: ')
        print(classifier.show_most_informative_features(10))

        now = time.time()
        print('{0}: Обучение модели завершено".. Выполнено за {1} cек \n'.format(Support.ConvertStampToTime(now), now - start_time))

        return  classifier

def test1():
    nl= Analytic()
    str1 = "Ну что сказать, я вижу кто-то наступил на грабли, Ты разочаровал меня, ты был натравлен."
    str2 = "#FollowFriday @France_Inte @PKuchly57 @Milipol_Paris for being top engaged members in my community this week :)"
    str3 = "@97sides CONGRATS :)yeaaaah yippppy!!!  my accnt verified rqst has succeed got a blue tick mark on my fb profile :) in 15 days"

    text = [str1, str2, str3]

    s = nl.Stemming(text)
    f = nl.CalculateWordsFrequency(s)
    print(freq_dist_pos.most_common(10))

    l = nl.Lemmatization(text)
    print()

def testModel():
    positive=[]
    positive.append("#FollowFriday @France_Inte @PKuchly57 @Milipol_Paris for being top engaged members in my community this week :)")
    positive.append("Who Wouldn't Love These Big....Juicy....Selfies :)")
    positive.append("@Bosslogic @amellywood @CW_Arrow @ARROWwriters Thank you! ")
    positive.append("@AquaDesignGroup Thank you for the shout out. Have a great Friday :)")
    positive.append("@x123456789tine @5SOS_FAHUpdates gotta love timezones :p")
    positive.append("@TomParker oh wow!! That is beautiful tom ")
    positive.append("Good morning, beautiful :)")
    positive.append("#FollowFriday @France_Inte @PKuchly57 @Milipol_Paris for being top engaged members in my community this week :)")
    positive.append("Who Wouldn't Love These Big....Juicy....Selfies :)")
    positive.append("@Bosslogic @amellywood @CW_Arrow @ARROWwriters Thank you! ")
    positive.append("@AquaDesignGroup Thank you for the shout out. Have a great Friday :)")
    positive.append("@x123456789tine @5SOS_FAHUpdates gotta love timezones :p")
    positive.append("@TomParker oh wow!! That is beautiful tom ")
    positive.append("Good morning, beautiful :)")
    positive.append("#FollowFriday @France_Inte @PKuchly57 @Milipol_Paris for being top engaged members in my community this week :)")
    positive.append("Who Wouldn't Love These Big....Juicy....Selfies :)")
    positive.append("@Bosslogic @amellywood @CW_Arrow @ARROWwriters Thank you! ")
    positive.append("@AquaDesignGroup Thank you for the shout out. Have a great Friday :)")
    positive.append("@x123456789tine @5SOS_FAHUpdates gotta love timezones :p")
    positive.append("@TomParker oh wow!! That is beautiful tom ")
    positive.append("Good morning, beautiful :)")


    negative=[]
    negative.append('hopeless for tmr :(')
    negative.append("Everything in the kids section of IKEA is so cute. Shame I'm nearly 19 in 2 months :(")
    negative.append('Dang starting next week I have \"work\" :(')
    negative.append('I feel lonely someone talk to me guys and girls :(')
    negative.append("I feel stupid\nI just can't seem to grasp the basics of digital painting and nothing I've been researching is helping any :(")
    negative.append("My Gran tho !!! She knew but didn't care to tell me :(")
    negative.append("@itsNotMirna I was so sad because Elhaida was robbed by the juries :( she came 10th in the televoting ")
    negative.append('hopeless for tmr :(')
    negative.append("Everything in the kids section of IKEA is so cute. Shame I'm nearly 19 in 2 months")
    negative.append('Dang starting next week I have \"work\" :(')
    negative.append('I feel lonely someone talk to me guys and girls :(')
    negative.append("I feel stupid\nI just can't seem to grasp the basics of digital painting and nothing I've been researching is helping any :(")
    negative.append("My Gran tho !!! She knew but didn't care to tell me :(")
    negative.append("@itsNotMirna I was so sad because Elhaida was robbed by the juries :( she came 10th in the televoting :(")
    
    nl= Analytic()
    tokens_pos = nl.Lemmatization(positive)
    tokens_neg = nl.Lemmatization(negative)

    model = nl.TrainSentimentsPredictionModel(tokens_pos, tokens_neg)

    path = fm.GetExecutingScriptDir()+'\\LocalData\\'
    fm.SavePickle(model, path, 'f1')
    model = fm.LoadPickle(path, 'f1')
    model.show_most_informative_features(10)

    print()


if __name__ == '__main__':
    #test1()
    testModel()