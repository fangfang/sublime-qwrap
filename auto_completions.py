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

#判断是否不可用的区间（注释、字符串内部 etc）
def in_invalid_region(view, region):
	scope_name = view.scope_name(region.begin())

	return scope_name.count('comment.block.js') + scope_name.count('comment.line.double-slash.js') + scope_name.count('string.quoted.single.js') + scope_name.count('string.quoted.double.js') + scope_name.count('string.regexp.js') + scope_name.count('text.html') - scope_name.count('source.js.embedded') 

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

	_keys = re.compile(r'([\[\].(){}])').sub(r'\\\1', _keys)

	if(_keys):
		#根据scope-chain找最近的ally（即赋值语句）

		pattern = "(^|\s+)" + _keys + "\s*(=(?!=))\s*.*"

		allies = find_in_region(view, pattern, 0, sel.begin()) #从近到远的allies

		for ally in allies:

			if(not in_invalid_region(view, ally)): #不能在无效区间
				ally_scope = get_current_scope(view, ally) #得到ally的最小作用域（闭包）

				#sel必须要在ally_scope之内
				if(ally_scope[0] <= sel.begin() and ally_scope[1] >= sel.end()):
					newKeys = view.substr(ally).strip()
					#严格上来讲这样替换会有问题，因为可能会切入字符串，不过90%可用就行了
					#字符串中恰好包含赋值的极少
					newKeys = re.compile('[,;]\s*\w+\s*=.*$').sub('', newKeys)
					
					if(newKeys.endswith(",") or newKeys.endswith(";")):
						newKeys = newKeys[:-1]

					print 'ally:' + newKeys
					newKeys = newKeys.split("=")[1].strip()+_surfix
					
					if(newKeys == keys):
						return keys
					else:
						return find_key_ally(view, newKeys, ally)

	return keys

def reduce_global_allies(keys):
	
	if(keyword_maps.get(keys) or keyword_maps.get('window.' + keys)): #如果已经有内容了，就返回吧
		return keys

	newKeys = keys

	for reducer in global_reducer:	
		r = re.compile(reducer[0])
		newKeys = r.sub(reducer[1], newKeys)
	
	if(newKeys == keys):
		return keys
	else:
		return reduce_global_allies(newKeys)

	return keys

class AutoComplations(sublime_plugin.EventListener):
	def __init__(self):
		self.scopes = []

	def on_query_completions(self, view, prefix, locations):
		
		jsscope = view.find_by_selector('source.js')
		if(not jsscope or not view.sel()):
			return []
		
		inputChar = view.substr(sublime.Region(locations[0]-1, locations[0]))
		
		line = view.substr(view.line(view.sel()[0]))
		if(not self.scopes or re.compile('function').match(line)):
			self.scopes = all_scopes(view)

		view.scopes = self.scopes

		keys = capture_input(view) or maybe_wrap(view)

		if(keys):
			if(inputChar == '('):
				keys = keys[:-1]

			keys = keys.split('.')
			key_prefix = []

			if(not inputChar == '('):
				keys.pop()

			#识别变量赋值： trim = QW.StringH.trim
			for key in keys:
				key_prefix.append(key)
				if(key):
					key_prefix = find_key_ally(view, '.'.join(key_prefix), view.sel()[0]).split('.')
			
			keys = key_prefix
			if(inputChar == '('):
				func = keys.pop()
			keys = '.'.join(keys)
			
			#规约规则
			'''
				document.body.childNodes -> __element__.childNodes -> __nodelist__
			'''
			print 'trigger :' + keys

			keys = reduce_global_allies(keys) 
			
			print 'actual :' + keys

			if(not is_brackets_input(view)): #不是输入 '('
				
				if keys:
					compeletions = keyword_maps.get(keys) or keyword_maps.get('.'.join(['window', keys])) or keyword_maps.get('__default')
				
				else:
					compeletions = keyword_maps.get('window')

				ret = []

				#if(func):

					#[compeletions.get(key) or compeletions.get(' '+key) or compeletions.update({key: [key]}) for key in view.extract_completions(func)]

				keys = compeletions.keys()
				keys.sort()

				for compeletion in keys:
					ret.append((compeletions.get(compeletion)[0] + " ",compeletion.strip()))

				return ret
			else: #输入 '('

				if(keys):
					compeletions = keyword_maps.get(keys) or keyword_maps.get('.'.join(['window', keys])) or keyword_maps.get('__default')
					compeletions = compeletions.get(func) or [""]
				else:
					compeletions = keyword_maps.get('window').get(func) or [""]
				
				if(func.startswith('function')):
					m = re.compile('\(.*?\)').search(func)
					if(m):
						compeletions.append(m.group(0)[1:-1])

				if(compeletions):
					compeletions = compeletions[1:] or [""]
					
					ret = []
					#print compeletions
					for compeletion in compeletions:
						ret.append(("(" + compeletion.replace('"', '') + ")",("" + compeletion + ")").replace('...)', '')))
					return ret
