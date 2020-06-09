class Autorisation:
    def __init__(self):
        pass

    def VkLogin(self):
        login = 'LOGIN' 
        password = 'PASSWORD'
        return login, password

    def DbConnect(self):
        #"mongodb+srv://Admin:Admin@democluster-p9jrv.gcp.mongodb.net/test?retryWrites=true&w=majority"
        #"mongodb+srv://Admin:Admin@cluster0-nbu3t.mongodb.net/test?retryWrites=true&w=majority" - reserve
        return "mongodb+srv://Admin:Admin@democluster-p9jrv.gcp.mongodb.net/test?retryWrites=true&w=majority"