# [sublime text2](http://www.sublimetext.com) 编辑器的 QWrap 插件

## 目前实现的功能：

### 自动短变量名

     (function(){

     ...

         QW.StringH.trim(str);
     })();

光标停留在trim那一行，按[tab]键之后成为

     (function(){
         var trim = QW.StringH.trim,
     ...

         trim(str);
     })();

如果 var trim = QW.StringH.trim 已存在，将不会重复生成声明

如果按[ctrl+tab]的话，生成的变量声明在最内层的作用域，否则在最外层作用域

如果一行有多个长变量名，每按一次[tab]切换一个长变量

如果只要替换一行中的指定长变量，可以将这个长变量选中后按[tab]

## 其他功能以后陆续添加

按需开发...