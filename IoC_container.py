class IoCContainer:
    instanceIoCList=[]
    singletonInstance=None
    __instance = None
    def __new__(cls, *args, **kwargs):
        if not cls.__instance:
            cls.__instance = super().__new__(cls, *args, **kwargs)
        return cls.__instance
    
    container= {}
    @staticmethod
    def registerIoC(data1, data2):
        IoCContainer.container[data1] = data2  
        return IoCContainer.container
    
    @staticmethod
    def providerIoC(key,patern):
            if key in IoCContainer.container:           
                if patern=="transient":                  
                    for k in IoCContainer.container:                          
                        if key==k :
                            v= IoCContainer.container[key]()
                            IoCContainer.instanceIoCList.append(v)
                            return v
                        
                if patern=="singleton":
                    value =IoCContainer.container[key]
                    class SingletonClass(value):
                        __instance2 = None

                        def __new__(cls, *args, **kwargs):
                            for i in IoCContainer.instanceIoCList:
                                pass
                            if len(IoCContainer.instanceIoCList) == 0 or not isinstance(i, value):
                                if not cls.__instance2:
                                    cls.__instance2 = value.__new__(cls, *args, **kwargs)
                                    IoCContainer.singletonInstance = cls.__instance2
                                    IoCContainer.instanceIoCList.append(IoCContainer.singletonInstance)
                                    return cls.__instance2
                            else:
                                return IoCContainer.singletonInstance

                    singleton1 = SingletonClass()
                    return singleton1
            
