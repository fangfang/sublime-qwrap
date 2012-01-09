#coding: utf8

import re

keyword_maps = {
	#默认的Object
	'__object' : {
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
		'slice' : ['slice (int[, int])', 'fromPos', 'fromPos, toPos'],
		'substring' : ['substring (int, [,int])', 'fromPos', 'fromPos, toPos'],
		'substr' : ['substr (int, [,int])', 'fromPos', 'fromPos, toPos'],
		'charAt' : ['charAt (int)', 'pos'],
		'charCodeAt' : ['charCodeAt (int)', 'pos'],
		'toLowerCase' : ['toLowerCase ()'],
		'toUpperCase' : ['toUpperCase ()'],
		'split' : ['split (string)', 'sep'],
		'search' : ['search (mixed)', 'substr', 'regex'],
		'indexOf' : ['indexOf (string)', 'substr'],
		'lastIndexOf' : ['lastIndexOf (string)', 'substr'],
		'match' : ['match (mixed)', 'substr', 'regex'],
		'replace' : ['replace (mixed, mixed)', 'substr, replacement', 'regex, replacement', 'regex, func'],
		'fromCharCode' : ['fromCharCode (int)', 'code'],
		'concat' : ['concat (string)', 'str']
	},
	'__array' : {
		' length' : ['length'],
		'toString' : ['toString ()'],
		'toLocaleString' : ['toLocaleString ()'],
		'join' : ['join (string)', 'sep'],
		'shift' : ['shift ()'],
		'unshift' : ['unshift (object)', 'item'],
		'pop' : ['pop ()'],
		'push' : ['push (object)', 'item'],
		'concat' : ['concat (mixed)', 'item', 'arr'],
		'slice' : ['slice (int[, int])', 'fromPos', 'fromPos, toPos'],
		'reverse' : ['reverse ()'],
		'sort' : ['sort ([function])', '', 'func', 'function(a, b){}'],
		'splice' : ['splice (int[, int, mixed])', 'fromPos', 'fromPos, toPos', 'fromPos, toPos, replacement']	
	},
	'__number' :{
		'toString' : ['toString ([int])', '', 'n']
	},
	'__date' : {
		'getDate' : ['getDate ()'],
		'getDay' : ['getDay ()'],
		'getFullYear' : ['getFullYear ()'],
		'getHours' : ['getHours ()'],
		'getMilliseconds' : ['getMilliseconds ()'],
		'getMinutes' : ['getMinutes ()'],
		'getMonth' : ['getMonth ()'],
		'getSeconds' : ['getSeconds ()'],
		'getTime' : ['getTime ()'],
		'getTimezoneOffset' : ['getTimezoneOffset ()'],
		'getUTCDate' : ['getUTCDate ()'],
		'getUTCDay' : ['getUTCDay ()'],
		'getUTCFullYear' : ['getUTCFullYear ()'],
		'getUTCHours' : ['getUTCHours ()'],
		'getUTCMilliseconds' : ['getUTCMilliseconds ()'],
		'getUTCMinutes' : ['getUTCMinutes ()'],
		'getUTCMonth' : ['getUTCMonth ()'],
		'getUTCSeconds' : ['getUTCSeconds ()'],
		'getYear' : ['getYear ()'],
		'parse' : ['parse (string)', 'date'],
		'setDate' : ['setDate (int)', 'day'],
		'setFullYear' : ['setFullYear (int)', 'year'],
		'setHours' : ['setHours (int)', 'hour'],
		'setMilliseconds' : ['setMilliseconds (int)', 'millisec'],
		'setMinutes' : ['setMinutes (int)', 'minutes'],
		'setMonth' : ['setMonth (int)', 'month'],
		'setSeconds' : ['setSeconds (int)', 'seconds'],
		'setTime' : ['setTime (int)', 'millisec'],
		'setUCTDate' : ['setUCTDate (int)', 'date'],
		'setUCTFullYear' : ['setUCTFullYear (int)', 'year'],
		'setUTCHours' : ['setUTCHours (int)', 'hour'],
		'setUTCMilliseconds' : ['setMilliseconds (int)', 'millisec'],
		'setUTCMinutes' : ['setUTCMinutes (int)', 'minutes'],
		'setUTCMonth' : ['setUTCMonth (int)', 'month'],
		'setUTCSeconds' : ['setUTCSeconds (int)', 'seconds'],
		'setYear' : ['setYear (int)', 'year'],
		'toGMTString' : ['toGMTString ()'],
		'toLocaleString' : ['toLocaleString ()'],
		'toString' : ['toString ()']
	},
	'__regex' : {
		' global' : ['global'],
		' ignoreCase' : ['ignoreCase'],
		' multiline' : ['multiline'],
		' lastIndex' : ['lastIndex'],
		' source' : ['source'],
		'test' : ['test (string)', 'str'],
		'exec' : ['exec (string)', 'str'],
		'toLocaleString' : ['toLocaleString ()'],
		'toString' : ['toString ()']
	},
	'window' : {
		' window'	: ['window'],
		' document' : ['document'],
		' location' : ['location'],
		' opener'	: ['opener'],
		' frames'	: ['frames []'],
		'open' : ['open (string[, string, string])', 'url', 'url, parent', 'url, parent, params'],
		'alert' : ['alert (text)', 'msg'],	
		'close' : ['close ()'],
		'confirm' : ['confirm (text)', 'msg'],
		'promot' : ['promot (text[, text])', 'text', 'text, default'],
		'setTimeout' : ['setTimeout (func[, int])', 'expression', 'expression, ims', 'handler', 'handler, ims'],
		'clearTimeout' : ['clearTimeout (int)', 'timer'],
		'setInterval' : ['setInterval (func[, int])', 'expression', 'expression, ims', 'handler', 'handler, ims'],
		'Date' : ['Date (mixed)', '', 'millisec', 'str', 'year, month, date', 'year, month, date, hours, minutes, seconds, millisec'],
		'Array' : ['Array (mixed)', '', 'len', 'item, ...'],
		'RegExp' : ['RegExp (string[, string])', 'str', 'str, extra'] 
	},
	'window.document' : {
		' title' : ['title'],
		' cookie' : ['cookie'],
		' body' : ['body'],
		' location' : ['location'],
		' selection' : ['selection'],
		' documentElement' : ['documentElement'],
		'write' : ['write (text)', 'text'],
		'createElement' : ['createElement (element)', 'element'],
		'getElementById' : ['getElementById (string)', 'id'],
		'getElementsByName'	: ['getElementsByName (string)', 'tagName']
	},
	'window.location' : {
		' href' : ['href'],
		' hostname' : ['hostname'],
		' hash' : ['hash'],
		' port' : ['port'],
		' pathname' : ['pathname'],
		' search' : ['search'],
		' protocol' : ['protocol'],
		'reload' : ['reload ()'],
		'replace' : ['replace (string)', 'url']	
	},
	'__element' : {
		' nodeType' : ['nodeType'],
		' tagName' : ['tagName'],
		' childNodes' : ['childNodes []'],
		' nextSilbing' : ['nextSilbing'],
		' parentNode' : ['parentNode'],
		'appendChild' : ['appendChild (element)', 'element'],
		'getElementsByClassName' : ['getElementsByClassName (string)', 'className'],
		'getElementsByTagName' : ['getElementsByTagName (string)', 'tagName'],
		'insertBefore' : ['insertBefore (element, element)', 'newNode, targetNode'],
		'removeChild' : ['removeChild (element)', 'element'],
		'replaceChild' : ['replaceChild (element, element)', 'newNode, oldNode'],
		'hasChildNodes' : ['hasChildNodes ()'],
		'getAttribute' : ['getAttribute (string)', 'key'],
		'setAttribute' : ['setAttribute (string, string)', 'key, value'],
		'removeAttribute' : ['removeAttribute (string)', 'key']	
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
		' NodeH' : ['NodeH'],
		' NodeW' : ['NodeW'],
		' Dom' : ['Dom'],
		' DomU' : ['DomU'],
		' EventTargetH' : ['EventTargetH'],
		' Selector' : ['Selector'],
		'g' : ['g (mixed)', 'id', 'element'],
		'W' : ['W (mixed)', 'element', 'elements', 'selector', 'html'],
		'NodeW' : ['NodeW (mixed)', 'element', 'selector'],
		'provide' : ['provide (mixed[, object])', 'module', 'module, obj'],
		'use' : ['use (string, function)', 'modules, callback'],
		'namespace' : ['namespace (string, [object])', 'str', 'str, obj'],
		'noConflict' : ['noConflict ()'],
		'loadJS' : ['loadJS (string, function, options)', 'url, succeed, options'],
		'loadJsonp' : ['loadJsonp (string, function, options)', 'url, succeed, options'],
		'loadCss' : ['loadCss (string)', 'url'],
		'error' : ['error (object, string)', 'obj, type']
	},
	#Wrap，当链式调用时触发
	'__wrap' : {
		'forEach' : ['forEach (function)', 'handler', 'function(o, i){}'],
		'map' : ['map (function)', 'handler', 'function(o, i){}'],
		'filter' : ['filter (function)', 'handler', 'function(o, i){}'],
		'first' : ['first ()'],
		'last' : ['last ()'],
		'item' : ['item (int)', 'index'],
		'toArray' : ['toArray ()']
	},
	'QW.ArrayH' : {
		'map' : ['map (array, function[, object])', 'arr, handler', 'arr, handler, pThis'],
		'forEach' : ['forEach (array, function[, object])', 'arr, handler', 'arr, handler, pThis'],
		'filter' : ['filter (array, function[, object])', 'arr, handler', 'arr, handler, pThis'],
		'some' : ['some (array, function[, object]', 'arr, handler', 'arr, handler, pThis'],
		'every' : ['every (array, function[, object]', 'arr, handler', 'arr, handler, pThis'],
		'indexOf' : ['indexOf (array, object)', 'arr, obj'],
		'lastIndexOf' : ['lastIndexOf (array, object)', 'arr, obj'],
		'contains' : ['contains (array, object)', 'arr, obj'],
		'clear' : ['clear (array)', 'arr'],
		'remove' : ['remove (array, object)', 'arr, obj'],
		'unique' : ['unique (array)', 'arr'],
		'reduce' : ['reduce (array, function, initial)', 'arr, handler', 'arr, handler, initial'],
		'reduceRight' : ['reduceRight (array, function, initial)', 'arr, handler', 'arr, handler, initial'],
		'expand' : ['expand (array)', 'arr'],
		'toArray' : ['toArray (array)', 'arrLike']
	},
	'QW.HashsetH' : {
		'union' : ['union (array, array)', 'arr, arr2'],
		'intersect' : ['intersect (array, array)', 'arr, arr2'],
		'minus' : ['minus (array, array)', 'arr, arr2'],
		'complement' : ['complement (array, array)', 'arr, arr2']	
	},
	'QW.ClassH' : {
		'createInstance' : ['createInstance (function[, args ...])', 'cls', 'cls, ...'],
		'extend' : ['extend (function, function)', 'cls, parent']	
	},
	'QW.FunctionH' : {
		'methodize' : ['methodize (function[, string])', 'func', 'func, attr'],
		'mul' : ['mul (function, int)', 'func', 'func, opts'],
		'rwrap' : ['rwrap (function, wrap[, mixed, bool])', 'func, wrapper', 'func, wrapper, opts', 'func, wrapper, opts, keepReturnValue'],
		'hook' : ['hook (function, string, function)', 'func, when, handler'],
		'bind' : ['bind (function, object[, ...])', 'func, pThis', 'func, pThis, arg0, ...'],
		'lazyApply' : ['lazyApply (function, object, array, int, function)', 'func, pThis, args, ims, checker']	
	},
	'QW.DateH' : {
		'format' : ['format (date, string)', 'date, pattern']	
	},
	'QW.HelperH' : {
		'rwrap' : ['rwrap (helper, wrap[, options])', 'helper, wrapper', 'helper, wrapper, config'],
		'gsetter' : ['gsetter (helper[, options])', 'helper', 'helper, config'],
		'mul' : ['mul (helper[, options])', 'helper', 'helper, config'],
		'methodize' : ['methodize (helper[, string, bool = false])', 'helper', 'helper, attr', 'helper, attr, preserveProps']	
	},
	'QW.ModuleH' : {
		' provideDomains' : ['provideDomains []'],
		'provide' : ['provide (mixed[, object])', 'module', 'module, obj'],
		'use' : ['use (string, function)', 'modules, callback'],
		'addConfig' : ['addConfig (string, options)', 'module, opts']			
	},
	'QW.ObjectH' : {
		'isString' : ['isString (object)', 'obj'],
		'isFunction' : ['isFunction (object)', 'obj'],
		'isArray' : ['isArray (object)', 'obj'],
		'isArrayLike' : ['isArrayLike (object)', 'obj'],
		'isObject' : ['isObject (object)', 'obj'],
		'isPlainObject' : ['isPlainObject (object)', 'obj'],
		'isWrap' : ['isWrap (object)', 'obj'],
		'isElement' : ['isElement (object)', 'obj'],
		'set' : ['set (object, mixed[, mixed])', 'obj, key, value', 'obj, arrProps, arrValues', 'obj, props'],
		'get' : ['get (object, mixed)', 'obj, key', 'obj, arrProps', 'obj, propJson'],
		'mix' : ['mix (object, object[, bool = false])', 'des, src', 'des, src, override'],
		'dump' : ['dump (object, array)', 'obj, keys'],
		'map' : ['map (object, function, object)', 'obj, handler, pThis'],
		'keys' : ['keys (object)', 'obj'],
		'values' : ['values (object)', 'obj'],
		'create' : ['create (object, options)', 'proto, opts'],
		'stringify' : ['stringify (object)', 'obj'],
		'encodeURIJson' : ['encodeURIJson (object)', 'obj']	
	},
	'QW.StringH' : {
		'trim' : ['trim (string)', 'str'],
		'mulReplace' : ['mulReplace (string, arr)', 'str, arr'],
		'format' : ['format (string[, string ...])', 'str, replacement, ...'],
		'tmpl' : ['tmpl (string, options)', 'str, opts'],
		'contains' : ['contains (string)', 'str'],
		'byteLen' : ['byteLen (string)', 'str'],
		'subByte' : ['subByte (string)', 'str'],
		'capitalize' : ['capitalize (string)', 'str'],
		'camelize' : ['camelize (string)', 'str'],
		'decamelize' : ['decamelize (string)', 'str'],
		'encode4Js' : ['encode4Js (string)', 'str'],
		'escapeChars' : ['escapeChars (string)', 'str'],
		'encode4Http' : ['encode4Http (string)', 'str'],
		'encode4Html' : ['encode4Html (string)', 'str'],
		'encode4HtmlValue' : ['encode4HtmlValue (string)', 'str'],
		'decode4Html' : ['decode4Html (string)', 'str'],
		'stripTags' : ['stripTags (string)', 'str'],
		'evalJs' : ['evalJs (string)', 'str'],
		'evalExp' : ['evalExp (string)', 'str'],
		'queryUrl' : ['queryUrl ([string])', '', 'str'],
		'decodeURIJson' : ['decodeURIJson (string)', 'str']
	},
	'QW.CustEvent' : {
		'createEvents' :  ['createEvents (object, mixed)', 'target, events']	
	},
	'QW.NodeH' : {
		'outerHTML' : ['outerHTML (element)', 'element'],
		'hasClass' : ['hasClass (element, string)', 'element, cls'],
		'addClass' : ['addClass (element, string)', 'element, cls'],
		'removeClass' : ['removeClass (element, string)', 'element, cls'],
		'replaceClass' : ['replaceClass (element, string, string)', 'element, oldCls, newCls'],
		'toggleClass' : ['toggleClass (element, string, string', 'element, cls1, cls2'],
		'show' : ['show (element)', 'element'],
		'hide' : ['hide (element)', 'element'],
		'empty' : ['empty (element)', 'element'],
		'toggle' : ['toggle (element)', 'element'],
		'isVisible' : ['isVisible (element)', 'element'],
		'getXY' : ['getXY (element)', 'element'],
		'setXY' : ['setXY (element, int, int)', 'element, x, y'],
		'setSize' : ['setSize (element, int, int)', 'element, w, h'],
		'setInnerSize' : ['setInnerSize (element, int, int)', 'element, w, h'],
		'setRect' : ['setRect (element, int, int, int, int)', 'element, x, y, w, h'],
		'setInnerRect' : ['setInnerRect (element, int, int, int, int)', 'element, x, y, w, h'],
		'getSize' : ['getSize (element)', 'element'],
		'getRect' : ['getRect (element)', 'element'],
		'nextSilbing' : ['nextSilbing (element[, string])', 'element', 'element, selector'],
		'previousSibling' : ['nextSilbing (element[, string])', 'element', 'element, selector'],
		'ancestorNode' : ['ancestorNode (element[, string])', 'element', 'element, selector'],
		'parentNode' : ['parentNode (element[, string])', 'element', 'element, selector'],
		'firstChild' : ['firstChild (element[, string])', 'element', 'element, selector'],
		'lastChild' : ['lastChild (element[, string])', 'element', 'element, selector'],
		'contains' : ['contains (element, mixed)', 'element, id', 'element, target'],
		'insertAdjacentHTML' : ['insertAdjacentHTML (element, string, string)', 'element, where, html'],
		'insertAdjacentElement' : ['insertAdjacentElement (element, string, element)', 'element, where, newEl'],
		'insert' : ['insert (element, string, element)', 'element, where, newEl'],
		'insertTo' : ['insertTo (element, string, element)', 'element, where, refEl'],
		'appendChild' : ['appendChild (element, element)', 'element, childEl'],
		'insertSiblingBefore' : ['insertSiblingBefore (element, element)', 'element, newEl'],
		'insertSiblingAfter' : ['insertSiblingAfter (element, element)', 'element, newEl'],
		'insertBefore' : ['insertBefore (element, element, element)', 'element, newEl, refEl'],
		'insertAfter' : ['insertAfter (element, element, element)', 'element, newEl, refEl'],
		'insertParent' : ['insertParent (element, element)', 'element, newEl'],
		'replaceNode' : ['replaceNode (element, element)', 'element, newEl'],
		'replaceChild' : ['replaceChild (element, element)', 'element, refEl, childEl'],
		'removeNode' : ['removeNode (element)', 'element'],
		'removeChild' : ['removeChild (element)', 'element, childEl'],
		'getAttr' : ['getAttr (element, string)', 'element, attr'],
		'setAttr' : ['setAttr (element, string, string)', 'element, attr, value'],
		'removeAttr' : ['removeAttr (element, string)', 'element, attr'],
		'query' : ['query (element, string)', 'element, selector'],
		'one' : ['one (element, string)', 'element, selector'],
		'getElementsByClass' : ['getElementsByClass (element, string)', 'element, cls'],
		'getValue' : ['getValue (element)', 'element'],
		'setValue' : ['setValue (element, string)', 'element, value'],
		'getHtml' : ['getHtml (element)', 'element'],
		'setHtml' : ['setHtml (element, value)', 'element, value'],
		'encodeURIForm' : ['encodeURIForm (element, string)', 'element, filter'],
		'isFormChanged' : ['isFormChanged (element, string)', 'element, filter'],
		'cloneNode' : ['cloneNode(element[, bool = false])', 'element, cloneChilds'],
		'removeStyle' : ['removeStyle (element, string)', 'element, style'],
		'getStyle' : ['getStyle (element, string)', 'element, style'],
		'getCurrentStyle': ['getCurrentStyle (element, string)', 'element, style'],
		'setStyle' : ['setStyle (element, string, string)', 'element, style, value'],
		'borderWidth' : ['borderWidth (element)', 'element'],
		'paddingWidth' : ['paddingWidth (element)', 'element'],
		'marginWidth' : ['marginWidth (element)', 'element'],
		'tmpl' : ['tmpl (element, options)', 'element, params'],			
	},
	'QW.EventTargetH' : {
		'on' : ['on (element, string, handler)', 'element, type, handler'],
		'un' : ['un (element, string, handler)', 'element, type, handler'],
		'delegate' : ['delegate (element, string, string, handler)', 'element, selector, type, handler'],
		'undelegate' : ['undelegate (element, string, string, handler)', 'element, selector, type, handler'],
		'fire' : ['fire (element, string)', 'element, type']		
	},
	'QW.Dom' : {

	},
	'QW.NodeW' : {
		#retouch gsetters
		'val' : ['val(element[, string])', 'element', 'element, value'],
		'html' : ['html(element[, string])', 'element', 'element, html'],
		'attr' : ['attr(element, string[, string])', 'element, key', 'element, key, value'],
		'css' : ['css(element, string[, string])', 'element, key', 'element, key, value'],
		'size' : ['size(element[, int, int])', 'element', 'element, w, h'],
		'xy' : ['xy(element[, int, int])', 'element', 'element, x, y']
	},
	'QW.DomU' : {
		#retouch from DomU
		'g' : ['g (element)', 'element'],
		'getDocRect' : ['getDocRect (document)', 'document'],
		'create' : ['create (string[, bool, document])', 'html, rfrag, doc'],
		'pluckWhiteNode' : ['pluckWhiteNode (nodeList)', 'list'],
		'isElement' : ['isElement (element)', 'element'],
		'ready' : ['ready (function[, document])', 'handler', 'handler, doc'],
		'rectContains' : ['rectContains (rectangle, rectangle)', 'rect1, rect2'],
		'rectIntersect' : ['rectIntersect (rectangle, rectangle)', 'rect1', 'rect2'],
		'createElement' : ['createElement (string[, options, document])', 'tagName', 'tagName, props', 'tagName, props, doc']		
	}
}

#copy QW to window
keyword_maps.get('window').update(keyword_maps.get('QW'))

#copy QW.sth to window.sth
for key in keyword_maps.keys():
	if(key.startswith('QW.')):
		keyword_maps.update({}.fromkeys(['window' + key[2:]], keyword_maps.get(key)))

#retouch NodeH to NodeW & Dom
keyword_maps.get('QW.Dom').update(keyword_maps.get('QW.DomU'))
keyword_maps.get('QW.Dom').update(keyword_maps.get('QW.NodeH'))
keyword_maps.get('QW.Dom').update(keyword_maps.get('QW.EventTargetH'))

def retouch_to_wrap(keyword):
	for key in keyword_maps.get(keyword).keys():
		rules = keyword_maps.get(keyword).get(key)
		rules = '|'.join(rules)
		rules = re.compile('\(element(,\s*)?').sub('(', rules)
		rules = re.compile('\|element(,\s*)?').sub('|', rules)
		rules = re.compile('\[,\s*').sub('[', rules)
		rules = rules.split('|')
		keyword_maps.get('__wrap').update({}.fromkeys([key], rules))

retouch_to_wrap("QW.NodeH")
retouch_to_wrap("QW.EventTargetH")
retouch_to_wrap("QW.NodeW")

keyword_maps.get('QW.NodeW').update(keyword_maps.get('QW.NodeH'))
keyword_maps.get('QW.NodeW').update(keyword_maps.get('QW.EventTargetH'))

_default = {}
_default.update(keyword_maps.get('__object'))
_default.update(keyword_maps.get('__number'))
_default.update(keyword_maps.get('__string'))

#update shortcuts
_shortcuts = {
	'__default' : _default,
	'document.location' : keyword_maps.get('window.location'),
	'window.Array' : keyword_maps.get('QW.ArrayH'),
	'window.Function' : keyword_maps.get('QW.FunctionH'),
	'window.String' : keyword_maps.get('QW.StringH'),
	'window.Date' : keyword_maps.get('QW.DateH'),
	'window.W' : keyword_maps.get('QW.NodeW')
}

keyword_maps.update(_shortcuts)

#类型等价的别名 (pattern, key) 注意替换的先后依赖次序
global_allies = [
	('document.body', '__element'),
	('__element.parentNode', '__element'),
	('__element.childNodes\[[^]]+\]', '__element')
]