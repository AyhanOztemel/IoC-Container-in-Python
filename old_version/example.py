from IoC_container import IoCContainer
container=IoCContainer()
print("container instance id--->",id(container))

container1=IoCContainer()
print("container1 instance id--->",id(container1))
class Abstract:
    def __init__(self):
        print("abtract")

class Concrete(Abstract):
    def __init__(self):
       print("conrete")
    @staticmethod    
    def write():
        print("This is a Concrate class write method")
        print("-------------------------------------------")

#iocContainer = IoCContainer()
IoCContainer.registerIoC(Abstract, Concrete)
#print(sozluk)

class Abstract2:
    def __init__(self):
        print("abtract2")

class Concrete2(Abstract2):
    def __init__(self):
        print("conrete2")
    @staticmethod    
    def write():
        print("This is a Concrate2 class write method")
        print("-------------------------------------------")
        
IoCContainer.registerIoC(Abstract2, Concrete2 )       
class Abstract3:
    def __init__(self):
        print("abtract3")

class Concrete3(Abstract3):
    def __init__(self):
        print("conrete3")
    @staticmethod    
    def write():
        print("This is a Concrate3 class write method")
        print("-------------------------------------------")

dictionary3=IoCContainer.registerIoC(Abstract3, Concrete3 )        
print("dictionary3----->",dictionary3)
print("-----------------*******----------------------")

instance_IoC3_1=IoCContainer. providerIoC(Abstract3,"singleton")
print("1-Abstract3-->singleton instance_IoC_1---->",id(instance_IoC3_1))
print("isinstance(instance_IoC3_1,Abstract3--->",isinstance(instance_IoC3_1,Abstract3))
print("isinstance(instance_IoC3-1,Concrete3--->",isinstance(instance_IoC3_1,Concrete3))
instance_IoC3_1.write()

instance_IoC3_2=IoCContainer. providerIoC(Abstract3,"singleton")
print("2-Abstract3-->singleton instance_IoC3_2--->",id(instance_IoC3_2))
print("isinstance(instance_IoC3_2,Abstract3--->",isinstance(instance_IoC3_2,Abstract3))
print("isinstance(instance_IoC3-2,Concrete3--->",isinstance(instance_IoC3_2,Concrete3))
instance_IoC3_2.write()

instance_IoC3_3=IoCContainer. providerIoC(Abstract3,"transient" )
print("3-Abstract3-->transient instance_IoC3_3--->",id(instance_IoC3_3))
print("isinstance(instance_IoC3_3,Abstract3--->",isinstance(instance_IoC3_3,Abstract3))
print("isinstance(instance_IoC3-3,Concrete3--->",isinstance(instance_IoC3_3,Concrete3))
instance_IoC3_3.write()

instance_IoC3_4=IoCContainer. providerIoC(Abstract3,"singleton" )
print("4-Abstract3-->singleton instance_IoC3_4--->",id(instance_IoC3_4))
print("isinstance(instance_IoC3_4,Abstract3--->",isinstance(instance_IoC3_4,Abstract3))
print("isinstance(instance_IoC3-4,Concrete3--->",isinstance(instance_IoC3_4,Concrete3))
instance_IoC3_4.write()

instance_IoC2_0=IoCContainer. providerIoC(Abstract2,"singleton" )
print("5-Abstract2-->singleton instance_IoC2-0--->",id(instance_IoC2_0))
print("isinstance(instance_IoC2_0,Abstract2--->",isinstance(instance_IoC2_0,Abstract2))
print("isinstance(instance_IoC2-0,Concrete2--->",isinstance(instance_IoC2_0,Concrete2))
instance_IoC2_0.write()

instance_IoC2_1=IoCContainer. providerIoC(Abstract2,"singleton" )
print("6-Abstract2-->singleton instance_IoC2-1--->",id(instance_IoC2_1))
print("isinstance(instance_IoC2_1,Abstract2--->",isinstance(instance_IoC2_1,Abstract2))
print("isinstance(instance_IoC2-1,Concrete2--->",isinstance(instance_IoC2_1,Concrete2))
instance_IoC2_1.write()

instance_IoC2_2=IoCContainer. providerIoC(Abstract2,"transient" )
print("7-Abstract2-->transient instance_IoC2-2--->",id(instance_IoC2_2))
print("isinstance(instance_IoC2_2,Abstract2--->",isinstance(instance_IoC2_2,Abstract2))
print("isinstance(instance_IoC2-2,Concrete2--->",isinstance(instance_IoC2_2,Concrete2))
instance_IoC2_2.write()

instance_IoC2_3=IoCContainer. providerIoC(Abstract2,"transient" )
print("8-Abstract2-->transient instance_IoC2-3--->",id(instance_IoC2_3))
print("isinstance(instance_IoC2_3,Abstract2--->",isinstance(instance_IoC2_3,Abstract2))
print("isinstance(instance_IoC2-3,Concrete2--->",isinstance(instance_IoC2_3,Concrete2))
instance_IoC2_3.write()

instance_IoC2_4=IoCContainer. providerIoC(Abstract2,"singleton" )
print("9-Abstract2-->singleton instance_IoC2-4--->",id(instance_IoC2_4))
print("isinstance(instance_IoC2_4,Abstract2--->",isinstance(instance_IoC2_4,Abstract2))
print("isinstance(instance_IoC2-4,Concrete2--->",isinstance(instance_IoC2_4,Concrete2))
instance_IoC2_4.write()

instance_IoC1=IoCContainer. providerIoC(Abstract,"singleton" )
print("10-Abstract-->singleton instance_IoC1---->",id(instance_IoC1))
print("isinstance(instance_IoC1,Abstract---->",isinstance(instance_IoC1,Abstract))
print("isinstance(instance_IoC1,Concrete---->",isinstance(instance_IoC1,Concrete))
instance_IoC1.write()

instance_IoC1_1=IoCContainer. providerIoC(Abstract,"transient" )
print("10-Abstract-->singleton instance_IoC1_1---->",id(instance_IoC1_1))
print("isinstance(instance_IoC1_1,Abstract---->",isinstance(instance_IoC1_1,Abstract))
print("isinstance(instance_IoC1_1,Concrete---->",isinstance(instance_IoC1_1,Concrete))
instance_IoC1.write()
for i in IoCContainer.instanceIoCList:
    print(id(i))
    
try: 
    instance_IoC1=IoCContainer. providerIoC(Abstract5)
except Exception as e:
    print(f"Error-->: {e}")
