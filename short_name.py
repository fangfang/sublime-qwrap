#coding: utf8

import sublime, sublime_plugin
import re

#初始化当前的scope，因为在html文件中的js可能是片段的
def init_scope(view, region):
	ranges_ = view.find_by_selector('source.js.embedded') #找到所有的js片段
	for range_ in ranges_:
		if(range_.contains(region)):
			return (view.line(range_.begin()).end(), region.begin())  
	return (0, region.begin())  


#判断当前光标之前有没有类似a.b.c这样的内容
def match_regions(view):
	regions = view.sel()
	ret = []
	for region in regions:
		if(region.empty()):
			line = view.line(region)
		else:
			line = region
		name = view.find("\w+(\.\w+)+", line.begin())
		if(name and name.end() <= line.end()):
			ret.append(name)

	return ret


#看看有没有定义过shortname
#形如 : trim = QW.StringH.trim 这样的格式
def find_shortname_defined(view, shortname, prefix, scope):
	defineds = view.find_all(shortname + '\s*=\s*' + prefix)
	for defined in defineds:
		if(defined.begin() >= scope[0] and defined.end() <= scope[1]): 
			#如果在当前scope中找到这样的定义，返回
			return defined
	return ()

#找到变量定义的地方
def find_defined_line(view, scope):
	pos = None;
	var_defs = view.find_all("var \w+")
	for var_def in var_defs:
		if(var_def.begin() >= scope[0] and var_def.end() <= scope[1]):
			return view.line(var_def)
	return pos

#找到作用域开始的地方
def find_begin_pos(view, scope):
	pos = scope[0];
	begin_defs = view.find_all("\{")
	for begin_def in begin_defs:
		if(begin_def.begin() >= scope[0] and begin_def.end() <= scope[1]):
			return begin_def.begin() + 1
	return pos	

def actual_in_scope(view, scope): #通过左右花括号的数量判断是否真的在当前的scope中
	lefts_ =  view.find_all('\{')
	rights_ = view.find_all('\}')

	n = 0
	
	for left_ in lefts_:
		if(left_.begin() >= scope[0] and left_.end() <= scope[1]):
			n = n + 1;
	for right_ in rights_:
		if(right_.begin() >= scope[0] and right_.end() <= scope[1]):
			n = n - 1;			
	
	return n > 0

#得到当前最接近的作用域位置
def find_current_scope(view, region, scope):
	scopes = view.find_all('function(\s+\w+?)?([^)]+)')
	current_scope = (scope[0], region.begin())
	for scope in scopes:
		if(scope.end() <= region.begin() and actual_in_scope(view, (scope.end(), region.end()))):
			current_scope = (scope.end(), region.begin())
			continue
	return current_scope

#找到全局作用域位置
def find_global_scope(view, region, scope):
	current_scope = (scope[0], region.begin())
	scope = view.find('function(\s+\w+?)?([^)]+)', scope[0]) #找到第一个function作用域
	if(scope and scope < region and actual_in_scope(view, (scope.end(), region.end()))):
		return (scope.end(), region.begin())
	return current_scope

class JsShortNameCommand(sublime_plugin.TextCommand):
	def run(self, edit, scope_type="current"):
		regions = match_regions(self.view)

		for region in regions:
			if(not region.empty()):
				fullName = self.view.substr(region)
				namespaces = fullName.split(".")

				shortName = namespaces[-1]
				prefix = ".".join(namespaces[0:-1])
				
				#如果有名字空间
				if(prefix):
					#取得scope的范围
					scope = init_scope(self.view, region)
					if(scope_type == "current"): #如果是局部作用域
						scope = find_current_scope(self.view, region, scope)
					else: #否则全局的
						scope = find_global_scope(self.view, region, scope)
					
					self.view.replace(edit, region, shortName)
					defined = find_shortname_defined(self.view, shortName, prefix, scope)

					if(not defined): #如果没有定义
						pos = find_defined_line(self.view, scope)
						if(pos != None):
							lineContents = self.view.substr(pos)
							pattern = re.compile("var\s*.+")
							newContents = pattern.sub("var " + shortName + " = " + fullName + ",", lineContents + '\n') 
							self.view.replace(edit, pos, newContents + lineContents.replace('var', '', 1))
						else:
							pos = find_begin_pos(self.view, scope)	
							self.view.insert(edit, pos, "\nvar " + shortName + " = " + fullName + ";\n")
					
