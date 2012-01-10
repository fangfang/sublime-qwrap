#coding: utf8

from keyword_maps import keyword_maps, global_reducer

#用户自定义提示添加在下面

user_maps = {
	
}

user_reducer = [
	
]

keyword_maps.update(user_maps)
global_reducer = global_reducer + user_reducer