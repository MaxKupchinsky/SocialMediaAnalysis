import vk_api
import math
import time
import datetime
import Support
import collections
import random
import copy
from  AutorizationData import Autorisation

class VkAdapter:
    def __init__(self):
        self.api = self.InitApi()

    # инициализация новой сессии апи
    def InitApi(self):
        authData = Autorisation()
        login, password = authData.VkLogin()

        vk_session = vk_api.VkApi(login, password)
        try:
            vk_session.auth(token_only=True)
        except vk_api.AuthError as error_msg:
            print(error_msg)
            return

        return vk_session.get_api()

    # Поиск активных групп по вхождению подстроки в названии (не больше 1000)
    def SearchGroups(self, title_sbstr, timeout = 5):
        if type(title_sbstr) is not list:
            title_sbstr = [title_sbstr]

        groups = []
        group_ids=set()

        start_time = time.time()
        stop_time = start_time + 60*timeout
        overtime = False
        str = "Поиск групп по подстрокам: {0}. Начато {1}".format(Support.CollectionToSeparatedString(title_sbstr), Support.ConvertStampToTime(start_time))
        print(str)

        group_fields_filters = 'city,country,place,description,members_count,counters,start_date,finish_date,can_see_all_posts,activity,status'

        for str in title_sbstr:
            response = self.api.groups.search(q=str, count = 1000)
            items = response['items']
            if items:
                print('Найдено групп: {0}'.format(len(items)))
                for raw_group in items:
                    if time.time() > stop_time:
                        overtime = True
                        break
                    if raw_group['is_closed'] == 0 and raw_group['id'] not in group_ids:
                        try:
                            response = self.api.groups.getById(group_id = raw_group['id'], fields = group_fields_filters)
                            if len(response) == 1:
                                group = response[0]
                                group_ids.add(group['id'])
                                groups.append(group)

                                now = time.time()
                                print('{0}: загружены данные для {1}'.format(Support.ConvertStampToTime(now), group['id']))
                            else:
                                print("При поиске группы по id: %id была найдена несколько/ни одной групп"% (raw_group['id']));
                        except:
                            now = time.time()
                            print('{0}:ОШИБКА  данные для {1} не были загружены корректно'.format(Support.ConvertStampToTime(now), raw_group['id']))
                            continue
        if overtime:
            print('Выполнение прервано, превышено время ожидания {0} минут'.format(timeout))

        now = time.time()
        print('{0}: Всего групп обработано: {1}. Выполнено за {2} cек \n'.format(Support.ConvertStampToTime(now), len(groups), now - start_time))
        return groups

    #Получение информации о пользователях-подписчиках по json с информацией о группе
    def GetGroupsSubscriberIds(self, groups, timeout = 25):
        if type(groups) is not list:
            groups = [groups]

        step = 1000
        unique_subscriber_ids = set()
        all_subscriber_ids =list()

        start_time = time.time()
        stop_time = start_time + 60*timeout
        overtime = False
        print("Поиск подписчиков групп/сообществ. Начато {0}".format(Support.ConvertStampToTime(start_time)))

        print('Сообществ к обработке: {0}'.format(len(groups)))
        for group in groups:
            id=group['id']
            if len(group)==0:
                 print('У группы %id нет подписчиков' %(id))
                 continue
           
            if not 'members_count' in group:
                print('У группы %id не было поля members_count' %(id))
                continue

            now = time.time()
            print('{0}:Cообщество id:{1} - {2} подписчиков'.format(Support.ConvertStampToTime(now), id, group['members_count']))
            iterations = math.ceil(group['members_count']/step)

            for i in range(0,iterations):
                if time.time() > stop_time:
                    overtime = True
                    break
                try:
                    response = self.api.groups.getMembers(group_id = id, count = step, offset = step*i)
                    if response['items']:
                        for subscriber_id in response['items']:
                            unique_subscriber_ids.add(str(subscriber_id))
                            all_subscriber_ids.append(str(subscriber_id))
                        now = time.time()
                        print('{0}:Получены id {1}-х {2} подписчиков'.format(Support.ConvertStampToTime(now), i+1, step))
                except:
                    now = time.time()
                    print('{0}:ОШИБКА  данные не были загружены корректно. Переход к следующей итерации'.format(Support.ConvertStampToTime(now)))
                    continue

            if overtime:
                break
            now = time.time()
            print('{0}:Идентификаторы подписчиков сообщества id:{1} получены \n'.format(Support.ConvertStampToTime(now), id, step))
        
        if overtime:
            print('Выполнение прервано, превышено время ожидания {0} минут'.format(timeout))
        subscribers = list(unique_subscriber_ids)
        now = time.time()
        print('всего подписчиков: {0}'.format(len(all_subscriber_ids)))
        print('{0} Получено {1} уникальных пользователей. Выполнено за {2} cек \n'.format(Support.ConvertStampToTime(now), len(subscribers), now - start_time))  

        return subscribers

    def FindUsers(self, filter,group_filter=None,  timeout = 15):
        
        start_time = time.time()
        stop_time = start_time + 60*timeout
        print("Поиск людей. Начато {0}".format(Support.ConvertStampToTime(start_time)))

        users=[]
        step = 1000
        response = self.api.users.search(q=filter, count = 1)
        if not 'items' in response:
            print('По поисковому запросу {0} не найдено пользователей'.format(str(filter)))
            return []

        iterations = math.ceil(response['count']/step)
        for i in range(0, iterations):
            response = self.api.users.search(q=filter, count = step, offset = i*step)
            if 'items' in response:
                users.extend(response['items'])

        print('По поисковому запросу {0} найдено {1} пользователей'.format(str(filter), len(users)))

        users_id_in_group=set()
        users_in_group =[]

        if group_filter!=None:
            groups =self.SearchGroups(group_filter, timeout*0.1)
            for group in groups:
                group_user_ids = self.GetGroupsSubscriberIds(group, timeout/2)
                for user in users:
                    if str(user['id']) in group_user_ids and user['id'] not in users_id_in_group:
                        users_id_in_group.add(user['id'])
                        users_in_group.append(user)
                if time.time() > stop_time:
                    break
            if users_in_group:
                users = users_in_group
        return users

    # получение полной информации профиля по id пользователя
    def GetUsersInfo(self, subscriber_ids):
        if type(subscriber_ids) is not list:
            subscriber_ids = [subscriber_ids]

        step = 900
        subscribers = {}
        subscriber_field_filters = 'verified,sex,bdate,city,country,home_town,has_photo,domain,has_mobile,contacts,site,education,universities,schools,status,last_seen,followers_count,common_count,occupation,nickname,relatives,relation,personal,connections,exports,activities,interests,music,movies,tv,books,games,about,quotes,can_post,can_see_all_posts,can_see_audio,screen_name,maiden_name,crop_photo,is_friend,career,military'

        start_time = time.time()
        print('{0}:Получены {1} идентификаторов к извлечению полной инфoрмации профилей'.format(Support.ConvertStampToTime(start_time), len(subscriber_ids)))
        iterations = math.ceil(len(subscriber_ids)/step)
        for i in range(0,iterations):
            percent = round((i/iterations)*100, 1)
            now = time.time()
            print('{0}:Обрабатываются {1}-e {2} идентификаторов. Всего готово: {3}%'.format(Support.ConvertStampToTime(now), i+1, step, percent))
            
            ids = subscriber_ids[i*step:(i+1)*step]
            ids_string = ','.join(str(s) for s in ids)
            response = self.api.users.get(user_ids = ids_string, fields=subscriber_field_filters)
            print('Анкет в ответе: {0}'.format(len(response)))
            
            tmp_subscribers ={}
            for subscriber in response:
                tmp_subscribers[str(subscriber['id'])]=subscriber
            if len(response)<len(ids):
                for id in ids:
                    if id not in tmp_subscribers:
                        response = self.api.users.get(user_ids = [id], fields=subscriber_field_filters)
                        tmp_subscribers[str(id)]=response[0]
            subscribers.update(tmp_subscribers)
        now = time.time()
        print('{0} Данные профилей пользователей извлечены. Выполнено за {1} cек'.format(Support.ConvertStampToTime(now), now - start_time))
        return subscribers

    def GetUserGroups(self, user_id):
        groups=[]
        step = 500
        group_fields_filters = 'city,country,place,description,members_count,counters,start_date,finish_date,can_see_all_posts,activity,status'

        try:
            response = self.api.groups.get(user_id = user_id)
            count = response['count']
            print('У пользователя id {0} найдено групп.{1} Получение'.format(user_id, count))

            iterations = math.ceil(count/step)

            for i in range(0,iterations):
                 response = self.api.groups.get(user_id = user_id, extended=1, fields =group_fields_filters,  count = step, offset = i*step)
                 groups.extend(response['items'])

        except:
            print('Ошибка. Не удалось получить полный список групп для пoльзователя id {0}'.format(str(user_id)))
        return groups

    def GetFriends(self, id):
        friends =[]
        step = 5000
        try:
            response = self.api.friends.search(user_id = id)
            count = response['count']
            now = time.time()
            print('{0} У пользователя {1} найдено {2} друзей'.format(Support.ConvertStampToTime(now), id, count))
            iterations = math.ceil(count/step)

            for i in range(0,iterations):
                response = self.api.friends.get(user_id = id, count = step, offset = i*step)
                if 'items' in response:
                    for friend in response['items']:
                        friends.append(str(friend))
        except Exception as e:
            if str(e).find('This profile is private') !=-1:
                print('Позьзователь скрыл список своих друзей')
            else:
                print('Неизвестная ошибка')

        return friends

    def GetFriendsGraph(self, id, depth, nodes, edges, stop_time):        
        id = str(id)
        if time.time() > stop_time:
            return     
        if id not in nodes:
            nodes.append(id)
        if depth==0:
            return

        friends = self.GetFriends(id)
        for friend in friends:
            if (id,friend) not in edges and (friend, id) not in edges:
                edges.append((id,friend))
            self.GetFriendsGraph(friend,depth-1, nodes, edges, stop_time)

    def GetRawFriendsGraph(self, name_id, ids, depth, timeout = 60):
        nodes=[]
        edges=[]
        start_time = time.time()
        stop_time = start_time + 60*timeout
        if type(ids) is not list:
            print('{0} Старт формирование графа для пользователя id: {1}'.format(Support.ConvertStampToTime(start_time), ids))
            self.GetFriendsGraph(ids, depth, nodes, edges,stop_time)
            now = time.time()
            if now > stop_time:
                print('Выполнение прервано, превышено время ожидания {0} минут'.format(timeout))
            print('{0} Сформировано {1} узлов и {2} ребер'.format(Support.ConvertStampToTime(now), len(nodes), len(edges)))
        else:
            ids_string = ','.join(str(s) for s in ids)
            print('{0} Получены ids пользователей: {1}'.format(Support.ConvertStampToTime(start_time), ids_string))
            for id in ids:
                tmp_nodes=[]
                tmp_edges=[]
                now = time.time()
                print('{0} Старт формирование графа для пользователя id: {1}'.format(Support.ConvertStampToTime(now), id))
                self.GetFriendsGraph(id, depth, tmp_nodes, tmp_edges,stop_time)           
                print('{0} Сформировано {1} узлов и {2} ребер'.format(Support.ConvertStampToTime(now), len(tmp_nodes), len(tmp_edges)))
                now = time.time()
                if now > stop_time:
                    print('Выполнение прервано, превышено время ожидания {0} минут'.format(timeout))
                    break

                for node in tmp_nodes:
                    if node not in nodes:
                        nodes.append(node)
                for edge in tmp_edges:
                    n1=edge[0]
                    n2=edge[1]
                    if (n1,n2) not in edges and (n2,n1) not in edges:
                        edges.append((n1,n2))
                now = time.time()
                print('{0} Граф для id {1} объединен с основным графом'.format(Support.ConvertStampToTime(now), id))
            
        now = time.time()
        print('{0} Граф построен. Всего сформировано {1} узлов и {2} ребер  Выполнено за {3} cек'.format(Support.ConvertStampToTime(now), len(nodes), len(edges), now - start_time))
        print('Начинается извлечение метаданных профилей, ожидайте завершения')

        info = self.GetUsersInfo(nodes)
        now = time.time()
        print('{0} Операция завершена. Общее время выполнения: {1} cек'.format(Support.ConvertStampToTime(now), now - start_time))

        return {'_id': name_id, 'source': 'vk', 'roots': ids, 'nodes': nodes, 'edges': edges, 'nodes_info': info}

    def GetRecordOffsetByDate(self, owner_id, date):
        offset = 0
        step = 100

        while True:
            offset+=step
            response = self.api.wall.get(owner_id = owner_id, count =1, offset = offset)
            if not 'items' in response:
                print('Произошло что-то плохое')
                return

            if not response['items']:
                print('В период на {0} в сообществе не было записей'.format(date))
                break

            tmp_date = response['items'][0]['date']
            n_date =Support.ConvertStampToTime(tmp_date)

            if not Support.CompareDatesFirstLess(date, tmp_date):
                break

        response = self.api.wall.get(owner_id = owner_id, count = step, offset = offset - step+1)
        i=0
        for post in response['items']:
            tmp_date = post['date']
            if not Support.CompareDatesFirstLess(date, tmp_date):
                break
            i+=1

        offset-=step-i
        #response = self.api.wall.get(owner_id = owner_id, count = 1, offset = offset)
        return offset
    
    def GetPostsInPeriod(self, owner_id, date_from, date_to, isGroup):
        step =50
        posts=[]

        if isGroup:
            if int(owner_id)>0:
                owner_id = -int(owner_id)

        if not Support.CompareDatesFirstLess(date_from,date_to):
            print('Ошибка. Дата начала периода больше даты конца периода')
            return
        
        start_time = time.time()
        print('{0} Старт получение постов за период с {1} по {2} для стены пользователя id:{3}'.format(Support.ConvertStampToTime(start_time),date_from, date_to, owner_id))

        offset_date_from = self.GetRecordOffsetByDate(owner_id,date_from)
        offset_date_to = self.GetRecordOffsetByDate(owner_id, date_to)

        now = time.time()
        print('{0} Найдено {1} записей. Начинается извлечение данных'.format(Support.ConvertStampToTime(now), (offset_date_from-offset_date_to+1)))
        iterations = math.ceil((offset_date_from-offset_date_to+1)/step)
        if iterations == 1:
            delta = offset_date_from - offset_date_to
            delta = delta if delta>0 else 1
            step = delta if step >delta else step

        for i in range(0,iterations):
            percent = round((i/iterations)*100, 1)
            now = time.time()
            print('{0}: Готовность: {1}%'.format(Support.ConvertStampToTime(now), percent))
            
            response = self.api.wall.get(owner_id = owner_id, count = step, offset = offset_date_to+ i*step)#
            if 'items' in response:
                posts.extend(response['items'])

        now = time.time()
        print('{0} Операция завершена. Общее время выполнения: {1} cек'.format(Support.ConvertStampToTime(now), now - start_time))
        return posts

    def GetCommentsUnderPosts(self, posts):
        if type(posts) is not list:
            posts = [posts]
        step = 100
        start_time = time.time()
        print('{0} Старт получение комментариев. Всего постов к обработке: {1}'.format(Support.ConvertStampToTime(start_time), len(posts)))

        results =[]
        n=0
        for post in posts:
            n+=1
            id = int(post['id'])
            owner_id = post['owner_id']
            now = time.time()
            print('{0} Старт получение комментариев под постом {1} ({2} из {3})со стены пользователя id:{4}'.format(Support.ConvertStampToTime(now), id, n, len(posts), owner_id))

            post_dict={}
            try:
                post_dict['parent_post'] = post
                response = self.api.wall.getComments(owner_id=owner_id, post_id = id,count=1)
                iterations = math.ceil(response['current_level_count']/step)

                comments=[]
                for i in range(0,iterations):
                    response = self.api.wall.getComments(owner_id=owner_id, post_id = id, need_likes=1, count=100, thread_items_count=10)
                    if 'items' in response:
                        comments.extend(response['items'])
                post_dict['comments'] = comments

                results.append(post_dict)
                now = time.time()
                print('{0} Комментарии получены'.format(Support.ConvertStampToTime(now)))
            except:
                print('{Ошибка. Комментарии не были полученыю Переход к следующей итерации')
                continue

        now = time.time()
        print('{0} Операция завершена. Общее время выполнения: {1} cек'.format(Support.ConvertStampToTime(now), now - start_time))
        return results

#VkAdapter

def testGetComments():
    owner_id = -169464030
    date_from ='15.05.2020'
    date_to =  '17.05.2020'

    vk = VkAdapter()
    groups = vk.SearchGroups('абстрактные мемы для элиты всех')
    owner_id = groups[0]['id']
    posts = vk.GetPostsInPeriod(owner_id,date_from,date_to, True)
    comments =vk.GetCommentsUnderPosts(posts[0])

    print()

def testFindUser():
    vk = VkAdapter()
    users = vk.FindUsers('Наталья Добровольская', 'Мировая живопись')#340089778
    groups = vk.GetUserGroups(users[0]['id'])#

    users_id=[]  
    for user in users:
        users_id.append(user['id'])
    users_info = vk.GetUsersInfo(users_id)
        
    print()

def testGroups():
    vk = VkAdapter()
    groups = vk.SearchGroups(["hata soni"], 0.1)
    random.shuffle(groups)

    subscriber_ids = vk.GetGroupsSubscriberIds(groups, 0.1)
    random.shuffle(subscriber_ids)

    subscribers = vk.GetUsersInfo(subscriber_ids)
    print()

def testGraph():       
    vk = VkAdapter()
    g = vk.GetRawFriendsGraph('simple_graph', ['155479601', '66811665'], 1, 15)
    print()

if __name__ == '__main__':
    #testGroups()
    #testGraph()
    #testGetComments()
    #testFindUser()
    print()
    
