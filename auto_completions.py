#coding: utf8

import sublime, sublime_plugin
import re
from keyword_maps import keyword_maps

def all_scopes(view):
	#找到所有的作用域
	ret = [(0, 999999)] #最大的作用域
	scopes = view.find_all('function(\s+\w+?)?([^)]+)')
	lefts_ = [(match.begin(), 1) for match in view.find_all('\{')]
	rights_ = [(match.begin(), -1) for match in view.find_all('\}')]

	all_ = lefts_ + rights_
	all_.sort()

	for scope in scopes:

		i = 0
		begin = None

		for one in all_: #每一个括号
		 	if(scope.end() <= one[0]):
		 		i = i + one[1]
		 		if(not begin and i == 1):
		 			begin = one[0]
		 		if(i == 0):
		 			break		 			 	
				
		
		if(i == 0):
			ret.append((begin, one[0]))

	return ret

#得到当前光标所在的作用域链
def get_scope_chain(view, region):
	scopes = all_scopes(view)
	ret = []
	for scope in scopes:
		if(scope[0] <= region.begin() and scope[1] >= region.end()):
			ret.append(scope)
	ret.reverse()

	return ret


#从当前输入位置找前一个字符判断是否是.或(
def is_brackets_input(view):
	sel = view.sel()[0] #取第一个selection
	line = view.line(sel)
	begin = line.begin()
	while begin < line.end():
		keys = view.find("[.(]", begin)
		if(not keys or keys.begin() > line.end()): #没找到
			break
		if(keys.end() == sel.begin()): #找到了
			return view.substr(keys) == '('
		begin = keys.end()
	return False

#从当前输入的位置地方往前找到全部的key
def capture_input(view):
	sel = view.sel()[0] #取第一个selection
	line = view.line(sel)
	begin = line.begin()
	while begin < line.end():
		keys = view.find("[,\[\]\w\"\'\/]+(\(.*?\))?(\.[,\[\]\w\"\'\/]+(\(.*?\))?)*([.(])?", begin)

		if(not keys or keys.begin() > line.end()): #没找到
			break
		if(keys.end() == sel.begin()): #找到了
			return view.substr(keys)
		begin = keys.end()
	return None

#从当前输入的位置往前找wrap
def capture_wrap(view):
	sel = view.sel()[0] #取第一个selection
	line = view.line(sel)
	begin = line.begin()
	while begin < line.end():
		keys = view.find("\(.*\)", begin)
		if(not keys or keys.begin() > line.end()): #没找到
			break
		if(keys.end()+1 == sel.begin()): #找到了
			return view.substr(keys)
		begin = keys.end()
	return None

#查找有木有 keys = ally 的赋值存在
def find_key_ally(view, keys):
	keys = keys.replace('[', '\[').replace(']','\]').replace('.','\.')
	if(keys):
		scopes = get_scope_chain(view, view.sel()[0])
		#根据scope-chain找最近的ally（即赋值语句）
		for scope in scopes: #从最里面往外找
			ally = view.find(keys + "\s*=\s*(new\s+)?[,\[\]\w\"\'\/]+(\(.*?\))?(\.[,\[\]\w\"\'\/]+(\(.*?\))?)*", scope[0])
			if(ally and ally.end() < scope[1]):
				ally_scope = get_scope_chain(view, ally)[0] #得到ally的最小作用域（闭包）
				#scope必须要在ally_scope之内，这样才能有效访问ally
				if(ally_scope[0] <= scope[0] and ally_scope[1] >= scope[1]):
					ally = view.substr(ally)
					if(ally.endswith(",")):
						ally = ally[:-1]
					return ally.split("=")[1].strip()

def unique(list): #唯一化并且要保证次序
	ret = []
	for item in list:
		if(item in ret):
			continue
		ret.append(item)
	return ret

class AutoComplations(sublime_plugin.EventListener):
	def __init__(self):
		self.toggle = False

	def on_query_completions(self, view, prefix, locations):

		jsscope = view.find_by_selector('source.js')
		if(not jsscope):
			return []
		keys = capture_input(view) or capture_wrap(view)

		if(keys):
			if(keys.endswith('(')):
				keys = keys[:-1]

			keys = keys.split('.')

			#识别变量赋值： trim = QW.StringH.trim

			ally_keys = '.'.join([find_key_ally(view, key) or key for key in keys]).split('.')

			while(ally_keys != keys):
				keys = ally_keys
				ally_keys = '.'.join([find_key_ally(view, key) or key for key in keys]).split('.')
				ally_keys = unique(ally_keys)

			func = keys.pop()

			keys = '.'.join(keys)

			if(keys.startswith('new Date(')):
				keys = "__date"
			
			if(keys.startswith('new Array(') or keys.startswith('[')):
				keys = "__array"

			if(re.compile("^\d+(.\d+)?").match(keys)):
				keys = "__number"
			
			if(keys.endswith('"') or keys.endswith("'")):
				keys = "__string"
			
			if(re.compile("\/.*\/[gim]?").match(keys)):
				keys = "__regex"

			print keys

			if(not keys):
				return []
			
			if(keys.endswith(')')):
				keys = "__wrap"
				func = None

			if(not is_brackets_input(view)): #不是输入 '('
				compeletions = keyword_maps.get(keys) or keyword_maps.get('__default')
				ret = []
				#print compeletions
				keys = compeletions.keys()
				keys.sort()
				for compeletion in keys:
					ret.append((compeletions.get(compeletion)[0] + " ",compeletion.strip()))

				if(func and func in [k.strip() for k in keys]):
					return []
				return ret
			else: #输入 '('
				compeletions = (keyword_maps.get(keys) or keyword_maps.get('__wrap') or {}).get(func) or keyword_maps.get('__default').get(func) or [""]
				
				if(compeletions):
					compeletions = compeletions[1:] or [""]
					
					ret = []
					#print compeletions
					for compeletion in compeletions:
						ret.append(("(" + compeletion + ")","" + compeletion + ")"))
					return ret
