import pymongo
from AutorizationData import Autorisation
from pymongo import MongoClient
import  collections
from bson.objectid import ObjectId
 
class DataBase:

    def __init__(self):
        self.db = self.InitDb()
        self.current_collection=None
    
    def InitDb(self):
        auth = Autorisation()
        connect = auth.DbConnect()
        cluster = MongoClient(connect)
        return cluster['SocialMediaData']

    def SetCurrentCollection(self,collection):
        if collection not in self.db.list_collection_names():
            print('Создана новая коллекция {0}'.format(collection))
        self.current_collection = self.db[collection]

    def __CollectionToWork(self,collection):
        if collection==None and self.current_collection == None:
            raise ValueError('Нет коллеции для работы')
        else:
            if collection==None:
                col = self.current_collection
            else:
                col = self.db[collection]
            return col

    def Insert(self, post, collection=None, findDoubles = True):
        coll=self.__CollectionToWork(collection)

        if isinstance(post, list):
            if not findDoubles:             
                coll.insert_many(post)
            else:
                for item in post:
                    if '_id' in item:
                        if coll.find_one({'_id': item['_id']}) != None:               
                            print('Элемент с _id:{0} уже есть в коллекции. Добaвление не осуществлено'.format(item['_id']))
                            continue
                    coll.insert_one(item)
        else:
            if '_id' in post and coll.find_one({'_id': post['_id']}) != None:
                print('Элемент с _id:{0} уже есть в коллекции. Добaвление не осуществлено'.format(post['_id']))
                return
            coll.insert_one(post)

    def DeleteById(self, id,collection=None):
        coll=self.__CollectionToWork(collection)
        coll.delete_one({'_id':id})

    def GetAll(self, collection=None):
        coll=self.__CollectionToWork(collection)

        cursor = coll.find()  
        result =[]
        for data in cursor.limit(0):
            result.append(data)
            
        return result

    def FindById(self,id,collection=None):
        coll=self.__CollectionToWork(collection)
        return coll.find_one({'_id':id})

    def UpdateById(self,id, value, collection=None):
        coll=self.__CollectionToWork(collection)
        coll.update_one({'_id':id}, {"$set":value})
#DataBase


def testDb():
    db = DataBase()
    post=[{'name': 111, 'ff': {'name': 111, 'ff': 'ddd'}}, {'name': 222}]
    db.SetCurrentCollection('SocialGraph')
    db.UpdateByName(111, {'name': 111, 'ff': 'dfdfd0'})
    print()

if __name__ == '__main__':
    testDb()

