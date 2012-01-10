#coding: utf8

import sublime, sublime_plugin
import re
from keyword_maps_user import keyword_maps, global_reducer

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
		 	if(scope.end() <= one[0]): #匹配在scope之后的括号，即function作用声明之后
		 		i = i + one[1]
		 		if(not begin and i == 1):
		 			begin = one[0]
		 		if(i == 0):
		 			break
		 	else:
		 		all_ = all_[1:] #抛弃外边的不用的，这样减少循环次数，因为all_和scopes都是排过序的 			 	
				
		
		if(i == 0):
			ret.append((begin, one[0]))

	return ret

#得到当前region所在的作用域链
def get_scope_chain(view, region):
	scopes = view.scopes
	ret = []
	for scope in scopes:
		if(scope[0] <= region.begin() and scope[1] >= region.end()):
			ret.append(scope)
		if(scope[1] < region.end()):
			break
	ret.reverse()

	return ret

#获得当前region作用域
def get_current_scope(view, region):
	return get_scope_chain(view, region)[0]

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
		keys = view.find("(?<=\))\.|(?<=^)\s*\.", begin)

		if(not keys or keys.begin() > line.end()): #没找到
			break
		if(keys.end() == sel.begin()): #找到了
			return "__wrap" + view.substr(keys)
		begin = keys.end()
	return None

#在当前区域中寻找和匹配指定模式，得到从后往前的一个数组
def find_in_region(view, pattern, begin, end):
	matches = view.find_all(pattern)
	ret = []
	for match in matches:
		if(match.begin() >= begin and match.end() <= end):
			ret.append(match)
	ret.reverse()
	return ret

#得到所有不可用的区间（注释、字符串内部 etc）
def in_invalid_region(view, region):
	invalid_regions = view.find_by_selector('comment.block.js, comment.line.double-slash.js, string.quoted.single.js, string.quoted.double.js, string.regexp.js, text.html - source.js')
	for invalid_region in invalid_regions:
		if(invalid_region.contains(region)):
			return True
	return False

#TODO: 得到完整的赋值表达式
def get_assign_expr(view, keys, scope):
	pass

#查找有木有 keys = ally 的赋值存在
def find_key_ally(view, keys, sel):
	_keys = keys
	_surfix = ''
	
	m = re.compile('.*(\[.*\])$').match(keys) #处理下标
	if(m):
		_surfix = m.group(1)
		_keys = keys[:-len(_surfix)]

	re.compile(r'([\[\].(){}])').sub(r'\\{\1}', _keys)

	if(_keys):

		#根据scope-chain找最近的ally（即赋值语句）

		pattern = "(^|\s+)" + _keys + "\s*=\s*(new\s+)?[,\[\]\w\"\'\/\{\}]+(\(.*?\))?(\.[,\[\]\w\"\'\/\{\}]+(\(.*?\))?(\[.*\])?)*"
		allies = find_in_region(view, pattern, 0, sel.begin()) #从近到远的allies

		for ally in allies:

			if(not in_invalid_scope(view, ally)): #不能在无效区间
				ally_scope = get_current_scope(view, ally) #得到ally的最小作用域（闭包）

				#sel必须要在ally_scope之内
				if(ally_scope[0] <= sel.begin() and ally_scope[1] >= sel.end()):
					newKeys = view.substr(ally).strip()

					if(newKeys.endswith(",")):
						newKeys = newKeys[:-1]
					
					newKeys = newKeys.split("=")[1].strip()+_surfix
					
					if(newKeys == keys):
						return keys
					else:
						return find_key_ally(view, newKeys, ally)

	return keys

def reduce_global_allies(keys):
	newKeys = keys

	for reducer in global_reducer:	
		r = re.compile(reducer[0])
		newKeys = r.sub(reducer[1], newKeys)
	
	if(newKeys == keys):
		return keys
	else:
		return reduce_global_allies(newKeys)

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
		self.scopes = []

	def on_query_completions(self, view, prefix, locations):
		
		line = view.substr(view.line(view.sel()[0]))
		if(not self.scopes or re.compile('function').match(line)):
			self.scopes = all_scopes(view)

		view.scopes = self.scopes

		jsscope = view.find_by_selector('source.js')
		if(not jsscope):
			return []
		keys = capture_input(view) or maybe_wrap(view)

		if(keys):
			if(keys.endswith('(')):
				keys = keys[:-1]

			keys = keys.split('.')
			key_prefix = []

			#识别变量赋值： trim = QW.StringH.trim
			for key in keys[:-1]:
				key_prefix.append(key)
				key_prefix = find_key_ally(view, '.'.join(key_prefix), view.sel()[0]).split('.')
			
			keys = key_prefix + keys[-1:]

			func = keys.pop()

			keys = '.'.join(keys)

			if(re.compile('^(new\s*)?Object\([^)]*\)$').match(keys) or keys.endswith('}')):
				keys = "__object"

			if(re.compile('^(new\s*)?Date\([^)]*\)$').match(keys)):
				keys = "__date"
			
			if(re.compile('^(new\s*)?Array\([^)]*\)$').match(keys) or re.compile('(Array\.prototype|\[\])\.slice\.call').match(keys) or keys.endswith(']') and (keys.startswith('[') or  keys.count('[') != keys.count(']'))):
				keys = "__array"
			
			if(re.compile('function\s*\w*\(.*\)').match(keys) and keys.endswith(')')):
				keys = "__function"

			if(re.compile("^\d+(.\d+)?$").match(keys)):
				keys = "__number"
			
			if(keys.endswith('"') or keys.endswith("'")):
				keys = "__string"
			
			if(re.compile('^(new\s*)?RegExp\([^)]*\)$').match(keys) or re.compile("\/.*\/[gim]?").match(keys)):
				keys = "__regex"

			if(re.compile("^(QW\.)?((DomU?\.)|(W?\.)|(NodeW?\.))?g\(.*?\)").match(keys) or re.compile('.*((create)|(get))Element(?!s)').match(keys)):
				keys = "__element"
			
			if(re.compile("^(QW\.)?(W|NodeW)?\(.*?\)([^)]*\)[^)]*)?$").match(keys)):
				keys = "__wrap"
			
			#规约规则
			'''
				document.body.childNodes -> __element__.childNodes -> __nodelist__
			'''
			keys = reduce_global_allies(keys) 
			print keys
			if(not is_brackets_input(view)): #不是输入 '('

				if keys:
					compeletions = keyword_maps.get(keys) or keyword_maps.get('.'.join(['window', keys])) or keyword_maps.get('__default')
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
					compeletions = keyword_maps.get(keys) or keyword_maps.get('.'.join(['window', keys])) or keyword_maps.get('__default')
					compeletions = compeletions.get(func) or [""]
				else:
					compeletions = keyword_maps.get('window').get(func) or [""]
				if(compeletions):
					compeletions = compeletions[1:] or [""]
					
					ret = []
					#print compeletions
					for compeletion in compeletions:
						ret.append(("(" + compeletion.replace('"', '') + ")","" + compeletion + ")"))
					return ret
