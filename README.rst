本地pip包服务器
==================

使用
----

.. code:: shell

    pip install -i server_url/simple package

原理
----

类似于代理。当用户请求的包没有时，会去官网边下载，边响应客户，同时保存包在本地。
