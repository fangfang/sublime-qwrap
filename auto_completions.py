#coding: utf8

import sublime, sublime_plugin
import re
from keyword_maps_user import keyword_maps, global_allies

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
		keys = view.find("(^|\s+)[,\[\]\w\"\'\/\{\}]+(\(.*?\))?(\.[,\[\]\w\"\'\/\{\}]+(\(.*?\))?)*([.(])?", begin)

		if(not keys or keys.begin() > line.end()): #没找到
			break
		if(keys.end() == sel.begin()): #找到了
			return view.substr(keys).strip()
		begin = keys.end()
	return None

#从当前输入的位置往前找wrap - 猜测有换行的不匹配的 ). 可能是 wrap，但不一定准确
def maybe_wrap(view):
	sel = view.sel()[0] #取第一个selection
	line = view.line(sel)
	begin = line.begin()
	while begin < line.end():
		keys = view.find("(^\s*|\))(\.\w*)?", begin)
		if(not keys or keys.begin() > line.end()): #没找到
			break
		if(keys.end() == sel.begin()): #找到了
			return "__wrap."
		begin = keys.end()
	return None

def find_in_scope(view, pattern, scope):
	matches = view.find_all(pattern)
	ret = []
	for match in matches:
		if(match.begin() >= scope[0] and match.end() <= scope[1]):
			ret.append(match)
	ret.reverse()
	return ret

#得到所有不可用的区间（注释、字符串内部 etc）
def in_invalid_scope(view, region):
	scopes = view.find_by_selector('comment.block.js, comment.line.double-slash.js, string.quoted.single.js, string.quoted.double.js, string.regexp.js')
	for scope in scopes:
		if(scope.contains(region)):
			return True
	return False

#TODO: 得到完整的赋值表达式
def get_assign_expr(view, keys, scope):
	pass

#查找有木有 keys = ally 的赋值存在
def find_key_ally(view, keys):
	keys = keys.replace('[', '\[').replace(']','\]').replace('.','\.').replace('(', '\(').replace(')', '\)').replace('{', '\{').replace('}', '\}');
	if(keys):
		sel = view.sel()[0]
		scopes = get_scope_chain(view, sel)
		#根据scope-chain找最近的ally（即赋值语句）
		for scope in scopes: #从最里面往外找
			pattern = "(^|\s+)" + keys + "\s*=\s*(new\s+)?[,\[\]\w\"\'\/\{\}]+(\(.*?\))?(\.[,\[\]\w\"\'\/\{\}]+(\(.*?\))?)*"
			allies = find_in_scope(view, pattern, (scope[0], sel.begin())) #从近到远的allies
			
			for ally in allies:
				if(not in_invalid_scope(view, ally)): #不能在无效区间
					ally_scope = get_scope_chain(view, ally)[0] #得到ally的最小作用域（闭包）
					#scope必须要在ally_scope之内，这样才能有效访问ally
					if(ally_scope[0] <= scope[0] and ally_scope[1] >= scope[1]):
						ally = view.substr(ally)
						if(ally.endswith(",")):
							ally = ally[:-1]
						return ally.split("=")[1].strip()

def replace_global_allies(keys):
	if(global_allies):
		for ally in global_allies:
			r = re.compile(ally[0])
			keys = r.sub(ally[1], keys)
	return keys

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
		keys = capture_input(view) or maybe_wrap(view)
		
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

			if(re.compile('^(new\s*)?Object\([^)]*\)$').match(keys) or keys.endswith('}')):
				keys = "__object"

			if(re.compile('^(new\s*)?Date\([^)]*\)$').match(keys)):
				keys = "__date"
			
			if(re.compile('^(new\s*)?Array\([^)]*\)$').match(keys) or keys.endswith(']')):
				keys = "__array"
			
			if(re.compile("^\d+(.\d+)?$").match(keys)):
				keys = "__number"
			
			if(keys.endswith('"') or keys.endswith("'")):
				keys = "__string"
			
			if(re.compile('^(new\s*)?RegExp\([^)]*\)$').match(keys) or re.compile("\/.*\/[gim]?").match(keys)):
				keys = "__regex"

			if(re.compile("^(QW\.)?((DomU?\.)|(W?\.)|(NodeW?\.))?g\(.*?\)").match(keys) or re.compile('.*((create)|(get))Element').match(keys)):
				keys = "__element"
			
			if(re.compile("^(QW\.)?(W|NodeW)?\(.*?\)").match(keys)):
				keys = "__wrap"
			
			keys = replace_global_allies(keys)
			
			if(not is_brackets_input(view)): #不是输入 '('

				if keys:
					compeletions = keyword_maps.get(keys) or keyword_maps.get('.'.join(['window', keys]))
					if(not compeletions): #如果不知道是什么类型
						compeletions = {}
						[compeletions.update(keys) for keys in [keyword_maps.get('__object'), keyword_maps.get('__number'), keyword_maps.get('__string')]]
				else:
					compeletions = keyword_maps.get('window')

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

				if(keys):
					compeletions = keyword_maps.get(keys) or keyword_maps.get('.'.join(['window', keys]))
					if(not compeletions): #如果不知道是什么类型
						compeletions = {}
						[compeletions.update(keys) for keys in [keyword_maps.get('__object'), keyword_maps.get('__number'), keyword_maps.get('__string')]]
					compeletions = compeletions.get(func) or [""]
				else:
					compeletions = keyword_maps.get('window').get(func) or [""]
				if(compeletions):
					compeletions = compeletions[1:] or [""]
					
					ret = []
					#print compeletions
					for compeletion in compeletions:
						ret.append(("(" + compeletion + ")","" + compeletion + ")"))
					return ret
