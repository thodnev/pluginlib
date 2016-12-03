'''
pluginlib: use dynamic python plugins with natural inheritance model

Usage:
1.  Define plugin root class by subclassing PluginBase:
    class SomeCls(PluginBase):
        ... some code here ...

2.  Write some plugins, that inherit from plugin root:
    class MyPlugin(SomeCls):
        ... extend/add/overwrite methods ...

3.  Get a mixed subclass with plugins as <Root>.PluginExtended:
    WithPlugins = SomeCls.PluginExtended
                  or
    class WithPlugins(SomeCls.PluginExtended):
        ... so could be used during further subclassing ...

*   The advantage is that SomeCls doesn't even need to know which plugins would
    be used in future. And it's still natural inheritance scheme for plugins.
*   Plugins must be imported before <Root>.PluginExtended is referenced,
    otherwise need to reference it again.
*   The order of plugins in resulting class is defined by order of set
    iteration, so don't rely on any ordering.
*   Attribute __name__ of resulting class will be <Root_name>PluginExtended,
    use subclassing scheme if crucial.
*   Plugin branches could be disabled/enabled/changed/etc by manipulating
    <Root>.__pluginextensions__ set and re-referencing <Root>.PluginExtended
'''

# TODO:
# ? order when ext-subclassing is arbitrary
# ? ext-subclass is derived from PluginBaseMeta
# - 'del' hack used to create PluginBase
# ? do we need to keep full list of plugins?
# + done: need to implement caching in PluginExtended property

__all__ = ['PluginBase']


class PluginBaseMeta(type):
    def __new__(mcls, name, bases, namespace):
        cls = super(PluginBaseMeta, mcls).__new__(mcls, name, bases, namespace)
        if not hasattr(cls, '__pluginextensions__'):  # parent class
            cls.__pluginextensions__ = {cls}  # set reflects lowest plugins
            cls.__pluginroot__ = cls
            cls.__pluginiscachevalid__ = False
        else:  # subclass
            assert not set(namespace) & {'__pluginextensions__',
                                         '__pluginroot__'}     # only in parent
            exts = cls.__pluginextensions__
            exts.difference_update(set(bases))  # remove parents
            exts.add(cls)  # and add current
            cls.__pluginroot__.__pluginiscachevalid__ = False
        return cls

    @property
    def PluginExtended(cls):
        # After PluginExtended creation we'll have only 1 item in set
        # so this is used for caching, mainly not to create same PluginExtended
        if cls.__pluginroot__.__pluginiscachevalid__:
            return next(iter(cls.__pluginextensions__))  # only 1 item in set
        else:
            name = cls.__pluginroot__.__name__ + 'PluginExtended'
            extended = type(name, tuple(cls.__pluginextensions__), {})
            cls.__pluginroot__.__pluginiscachevalid__ = True
            return extended


# 2.x compatible creation of class from metaclass
# Needed to make it simply inheritable, with no need to specify meta each time
PluginBase = PluginBaseMeta(
    'PluginBase', (object,), {'__metaclass__': PluginBaseMeta})
del PluginBase.__pluginextensions__  # dirty hack to avoid being plugin root

# Test below
if __name__ == '__main__':
    def ext(cls):
        e = cls.__pluginextensions__
        res = '{}:  {}'.format(cls.__pluginroot__.__name__,
                               sorted(e, key=lambda c: c.__name__))
        print(res)

    tree = '''\tPLUGIN TREE
    R o o t       OtherRoot
      /|\             |
     / | \            |
    A  B  C       OtherSub
    | /|
    |/ |
    D  E
    |
    |
    F
    '''
    print(tree)

    class Root(PluginBase):
        pass
    ext(Root)

    class OtherRoot(PluginBase):
        pass
    ext(Root)
    ext(OtherRoot)

    class OtherSub(OtherRoot):
        pass
    ext(OtherSub)

    class A(Root):
        pass

    class B(Root):
        pass

    class C(Root):
        pass
    ext(C)

    class D(A, B):
        pass
    ext(D)

    class E(B):
        pass
    ext(E)

    class F(D):
        pass
    ext(F)

    XT = F.PluginExtended
    XT2 = E.PluginExtended
    print('Same? (T)', XT is XT2)

    class ETC(F):
        pass
    XT3 = E.PluginExtended
    print('Now cache should be rebuilt. Same? (F)', XT3 is XT2)
