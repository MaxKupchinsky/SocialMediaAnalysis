from  VkApiAdapter import VkAdapter
from DbAdapter import DataBase
from GraphSupport import GraphManager
from AnalyticKit import Analytic
import FileManager as fm
import GraphSupport as graph
import matplotlib.pyplot as plt

def testGetVkCommentsAndSendToDb():
    date_from ='16.05.2020'
    date_to =  '17.05.2020'
    search_string = 'СтопКоронавирус'

    data =[]
    vk = VkAdapter()
    groups = vk.SearchGroups(search_string,1)
    for group in groups:
        owner_id = group['id']
        posts = vk.GetPostsInPeriod(owner_id,date_from,date_to, True)
        comments =vk.GetCommentsUnderPosts(posts)
        data.extend(comments)

    db = DataBase()
    db.SetCurrentCollection('{0}_{1}:{2}'.format(search_string, date_to,date_from))
    db.Insert(data)

    print()


def testGetVkGraphAndAddToDb():
    vk = VkAdapter()
    raw_graph0 = vk.GetRawFriendsGraph('sample_graph', ['155479601', '66811665'], 1)
    raw_graph1 = vk.GetRawFriendsGraph('ilia_depth1', ['66811665'], 1)
    raw_graph2 = vk.GetRawFriendsGraph('maxim_depth1', ['155479601'], 1)
    raw_graph3 = vk.GetRawFriendsGraph('maxim_depth2', ['155479601'], 2)

    db = DataBase()
    db.SetCurrentCollection('RawSocialGraph')
    db.Insert(raw_graph0)
    db.Insert(raw_graph1)

    db.Insert([raw_graph1,raw_graph2,raw_graph3])

    print()


def testVisualizeGraphWithGephi():
    db = DataBase()
    db.SetCurrentCollection('RawSocialGraph')
    sg1 = db.FindById('sample_graph')
    sg2 = db.FindById('maxim_depth1')

    graphics = GraphManager()
    graphics.ShowGraph(sg1)
    graphics.ShowGraph(sg2)
    print()

def testMakeAndVisualiseNxGraph():
    db = DataBase()
    db.SetCurrentCollection('RawSocialGraph')
    sg1 = db.FindById('ilia_depth1')
    sg2 = db.FindById('maxim_depth1')

    manager = GraphManager()
    g = manager.NetworxGraph([sg1,sg2], label_filters= ['first_name', 'last_name'])
    manager.ShowGraph(g)
    
    print()

def testOpenLocalFilesAndSendToDb():
    path = 'LocalData/corpora/twitter_samples/'
    file1 = 'positive_tweets.json'
    file2 = 'negative_tweets.json'
    file3 = 'tweets.20150430-223406.json'
    jfile = fm.OpenJson(path+file3)
   
    db = DataBase()
    db.SetCurrentCollection('TwitterSamples')
    db.Insert(jfile, findDoubles=False)

    print()

def testSaveToFile():
    db = DataBase()
    db.SetCurrentCollection('RawSocialGraph')
    sample_graph = db.FindById('sample_graph')

    manager = GraphManager()
    graph = manager.NetworxGraph(sample_graph, label_filters= ['first_name', 'last_name'])

    path = fm.GetExecutingScriptDir()+'\\LocalData\\'
    manager.SaveNgGraphToJson(graph, path)
    print()

def testLemmatizeData():
    db = DataBase()
    db.SetCurrentCollection('TwitterSentimentsData')
    
    #positive_tweets = db.FindById('positive_tweets')
    #positive_text=[]
    #for tweets in positive_tweets['items']:
    #    positive_text.append(tweets['text'])

    negative_tweets = db.FindById('negative_tweets')
    negative_text=[]
    for tweets in negative_tweets['items']:
        negative_text.append(tweets['text'])

    nl = Analytic()
    
    #positive_tokens = nl.Lemmatization(positive_text)
    #pos_dict = {'_id': 'positive_lemmatized_tokens', 'source': 'twitter', 'items': positive_tokens}
    #db.Insert(pos_dict)

    negative_tokens = nl.Lemmatization(negative_text)
    neg_dict = {'_id': 'negative_lemmatized_tokens', 'source': 'twitter', 'items': negative_tokens}
    db.Insert(neg_dict)


def testTrainPredictiveModel():
    nl = Analytic()
    db = DataBase()
    db.SetCurrentCollection('TwitterSentimentsData')

    positive_tokens = db.FindById('positive_lemmatized_tokens')['items']
    negative_tokens = db.FindById('negative_lemmatized_tokens')['items']
    all_tokens = positive_tokens + negative_tokens

    pos_freq = nl.CalculateWordsFrequency(positive_tokens)
    print(pos_freq.most_common(10))

    neg_freq = nl.CalculateWordsFrequency(negative_tokens)
    print(neg_freq.most_common(10))

    all_freq = nl.CalculateWordsFrequency(all_tokens)
    print(all_freq.most_common(10))

    model = nl.TrainSentimentsPredictionModel(positive_tokens, negative_tokens)
    path = fm.GetExecutingScriptDir()+'\\LocalData\\'
    fm.SavePickle(model, path, 'SentimentsPredictionModelLemmatized')
    print()

def testClassifier():
    nl = Analytic()

    path = fm.GetExecutingScriptDir()+'\\LocalData\\'
    name = 'SentimentsPredictionModelLemmatized'
    model = fm.LoadPickle(path, name)

    custom_text = []
    custom_text.append("I ordered just once from TerribleCo, they screwed up, never used the app again.")
    custom_text.append("Glad to see you!")
    nl.Classify(model, custom_text)


    model = nl.Classifier(model)
    
   
    custom_tokens = nl.Lemmatization(custom_text)
    model_tokens = nl.GetDictionaryForModel([custom_tokens])

    print(custom_text, model.classify(dict([token, True] for token in custom_tokens[0])))
    #cl = model.classify(model_tokens)

    #print(custom_text)


def SomeVeirdShit():
    vk = VkAdapter()
    #sg1 = vk.GetFullFriendsGraph('sample_graph', ['155479601'], 1, ['id'], 15)
    #sg2 = vk.GetFullFriendsGraph('sample_graph', ['66811665'], 1, ['id'], 15)

    #g1=graph.nx.Graph()
    #g1.add_edges_from(sg1['edges'])

    #g2=graph.nx.Graph()
    #g2.add_edges_from(sg2['edges'])

    #g['nodes'].append('666000666')
    #graph.DrawGraph(g)
    #g1 = g['nodes']
    #gg = vk.GetFullFriendsGraph('sample_graph', g1, 1, ['id', 'first_name', 'last_name'], 15)

    #graph.DrawGraph(gg)
    
    #p= {'_id': 111, 'g':'fdf'}


    db = DataBase()
    db.SetCurrentCollection('SocialGraph')
    sg0 = db.FindById('sample_graph')
    g0=graph.nx.Graph()
    g0.add_edges_from(sg0['edges'])



    #g12 = graph.nx.compose(g1,g2)
    d1 =  graph.nx.average_neighbor_degree(g0)
    graph.nx.draw(g12)
    plt.show()

    graph.foo1(g)

    db.UpdateById(111, {'e': 'fffs'})
    db.DeleteById(111)
    g2 = db.FindById('sample_graph')
    print()

def Demo1():
    db = DataBase()
    vk = VkAdapter()
    manager = GraphManager()

    db.SetCurrentCollection('RawSocialGraph') # выбираем коллекцию в бд для работы
    #g1 = db.FindById('maxim_depth2')# ищем набор данных по id
    #manager.ShowGraph(g1)# отправляем граф (в данном случае сырой, т.е. состоящий из метаданных вк)
    ##на вывод приложению Gephi

    #users = vk.FindUsers('Наталья Добровольская', 'Мировая живопись', 10)#340089778
    ## ищем id пользователей по подстроке '...' , которые подписаны на группы с подстрокой 
    ## в названии '...'  не более чем за 10 минут   
    id = str(340089778)#str(users[0]['id']) #
    print('По запросу найден id:'+ str(id))

    groups = vk.GetUserGroups(id)# получаем полный список групп пользователя
    for group in groups:
        print(group['name'] + ' ' + str(group['members_count']))
    
    users_info = vk.GetUsersInfo(id)# полная информация профиля
    print('Город: '+ users_info[id]['city']['title'] + ' Дата рождения' + users_info[id]['bdate'])

    g2 = vk.GetRawFriendsGraph('dnu_depth1',id, 1)# вытаскиваем из вк граф друзей глубины 1
    db.Insert(g2) # добавляем сырой граф в коллекцию. (Показать в монго)
    g3 = db.FindById('maxim_depth1')# тащим из бд уже заранее подготовленный сырой граф по Максим Купчинский

    ng = manager.NetworxGraph([g2,g3], ['first_name', 'last_name'])# Объединяем два сырых графа
    # и делаем из них один аналитический
    path = fm.GetExecutingScriptDir()+'\\LocalData\\'
    manager.SaveNgGraphToJson(ng, path)# Сохраняем аналитический граф на диск в формате json

    manager.ShowGraph(ng)# Отправляем аналитический граф на отрисовку

    date_from ='20.05.2020'
    date_to =  '21.05.2020'
    search_string = 'СтопКоронавирус'

    data =[]
    groups = vk.SearchGroups(search_string,1) # поиск групп по подстроке
    for group in groups:
        owner_id = group['id']
        posts = vk.GetPostsInPeriod(owner_id,date_from,date_to, True)# Получение записей на стене сообществ
        # за указанный период
        comments =vk.GetCommentsUnderPosts(posts)#Извлечение комментариев под ранее найденными записями
        data.extend(comments)

    # создаем новую коллекцию в бд и передаем туда посты и комментарии
    db.SetCurrentCollection('{0}_{1}:{2}'.format(search_string, date_to,date_from))
    db.Insert(data)

    print()

def foo():
    db = DataBase()
    vk = VkAdapter()
    manager = GraphManager()

    data=db.GetAll('TwitterSamples')

    dd = db.FindById('sample_graph', 'RawSocialGraph')

    graph1 = vk.GetRawFriendsGraph('g1', 155479601, 1)
    graph2 = vk.GetRawFriendsGraph('g2', 11503783, 1)
    graph3 = vk.GetRawFriendsGraph('g3', 340089778, 1)
    ng = manager.NetworxGraph([graph1,graph2,graph3], ["id"])

    d1 =  graph.nx.degree_centrality(ng)

    manager.ShowGraph(ng)
    print()



if __name__ == '__main__':
    #testGetVkGraphAndAddToDb()
    #testVisualizeGraphWithGephi()
    #testMakeAndVisualiseNxGraph()
    #testGetVkCommentsAndSendToDb()
    #testOpenLocalFilesAndSendToDb()
    #testSaveToFile()
    #Demo1()
    #foo()
    #testLemmatizeData()
    #testTrainPredictiveModel()
    testClassifier()
