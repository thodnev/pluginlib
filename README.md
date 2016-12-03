## pluginlib
######Dynamic Python plugins with natural inheritance model. Python 2.x and 3.x supported.######

#####A block diagram of how it looks like#####
The architecture is similar to plugin system used in Eclipse.

Plugins work as simple client classes, extending base class functionality by usual inheritance. 
At the moment of coding base class, you could even not know which plugins would be used. 
But base class always knows who inherits from it because of some metaclass magic.

And at request it builds class, which inherits from the plugins lowest on the tree.
The same holds true for plugins —  one plugin could extend another plugin.
It works the same as if you already know what that plugin classes are, except that you need not to know.

![A simple illustration of how it works](https://cloud.githubusercontent.com/assets/16870636/20856736/4be00bb2-b91f-11e6-8d68-ad167e3c6a54.png)

Usage:

1.  Define plugin root class by subclassing `PluginBase`:
    ```python
    class SomeCls(PluginBase):
        ... some code here ...
    ```

2.  Write some plugins, that inherit from plugin root:
    ```python
    class MyPlugin(SomeCls):
        ... extend/add/overwrite methods ...
    ```

3.  Get a mixed subclass with plugins as `<Root>.PluginExtended`:
    ```python
    WithPlugins = SomeCls.PluginExtended
    ```
    or
    ```python
    class WithPlugins(SomeCls.PluginExtended):
        ... so could be used during further subclassing ...
    ```



*   The advantage is that `SomeCls` doesn't even need to know which plugins would
    be used in future. And it's still natural inheritance scheme for plugins.

*   Plugins must be imported before `<Root>.PluginExtended` is referenced,
    otherwise need to reference it again.

*   The order of plugins in resulting class is defined by order of set
    iteration, so don't rely on any ordering.

*   Attribute `__name__` of resulting class will be `<Root_name>PluginExtended`,
    use subclassing scheme if crucial.

*   Plugin branches could be disabled/enabled/changed/etc by manipulating
   ` <Root>.__pluginextensions__` set and re-referencing `<Root>.PluginExtended`.
