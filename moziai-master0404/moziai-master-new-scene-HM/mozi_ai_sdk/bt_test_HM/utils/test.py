import  re
a = 'F16-A #07'
# a = '闪电 #5'
# b = int(re.sub('\D', '', a))
# print(b)
c=int(a.split('#')[1])
print(c)
# print(type(c))
'''
latitude='19.9345274245098', longitude='124.017702269376'
latitude='18.8527511210967', longitude='123.27120415328'
latitude='19.2245416178875', longitude='124.282096641003'

latitude='20.4712090531307', longitude='123.478824034918'
latitude='19.1204421036342', longitude='123.100844554812'
latitude='19.4181756401822', longitude='123.544356825938'
'''
# latitude='21.7210023818112', longitude='124.736772532602'
# latitude='18.5644868169818', longitude='121.9914498721'

s='1135型克里瓦克级II导弹护卫舰[1135级“风暴海燕”] #1501'
a='护卫舰' in s
print(a)

['DDG-79“奥斯卡奥斯丁号”阿利伯克级Flight II导弹驱逐舰', 'CG 70 “伊利湖号”提康德罗加级巡洋舰 ', 'DDG-79“奥斯卡奥斯丁号”阿利伯克级Flight II导弹驱逐舰', 'CVN 76 “里根号”尼米兹级航空母舰', 'CG 70 “伊利湖号”提康德罗加级巡洋舰 ']