#coding: utf8

keyword_maps = {
	#默认的Object
	'__default' : {
		#properties前面加一个空格，这样auto_complete中可以排序在methods前面
		' constructor' : ['constructor'],
		' prototype' : ['prototype'],
		'hasOwnProperty': ['hasOwnProperty (string)', 'str'],
		'isPrototypeOf' : ['isPrototypeOf (object)', 'obj'],
		'propertyIsEnumerable' : ['propertyIsEnumerable (string)', 'str'],
		'toString' : ['toString ()'],
		'valueOf' : ['valueOf ()']
	},
	'__string' :{
		'todo' : ['add string methods']
	},
	'__array' : {
		'todo' : ['add array methods']	
	},
	'__number' :{
		'todo' : ['add number methods']
	},
	'__date' : {
		'todo' : ['add date methods']
	},
	'__regex' : {
		'todo' : ['add regex methods']
	},
	'QW' : {
		' ObjectH' : ['ObjectH'],
		' StringH' : ['StringH'],
		' ArrayH' : ['ArrayH'],
		' HashsetH' : ['HashsetH'],
		' ModuleH' : ['ModuleH'],
		' HelperH' : ['HelperH'],
		' FunctionH' : ['FunctionH'],
		' DateH' : ['DateH'],
		' CustEvent' : ['CustEvent'],
		' ClassH' : ['ClassH'],
		' Browser' : ['Browser'],
		' VERSION' : ['VERSION'],
		' RELEASE' : ['RELEASE'],
		' PATH'	: ['PATH'],
		'namespace' : ['namespace (string, [object])', 'str', 'str, obj'],
		'noConflict' : ['noConflict ()']	
	},
	#Wrap，当).（链式调用）时触发
	'__wrap' : {
		'g' : ['g () [queryer]'],
		'one' : ['one () [queryer]'],
		'query' : ['query (selector) [queryer]', 'selector'],

	},
	'QW.StringH' : {
		'trim' : ['trim (string)', 'str']
	}
}