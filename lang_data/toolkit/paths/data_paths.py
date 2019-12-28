from os.path import exists, isdir, isabs, dirname


class DataPaths:
    def __init__(self, base_dir, DPaths):
        self.D = {}
        self.LNotFound = []

        for key, path in list(DPaths.items()):
            self._set_data_dir(base_dir, key, path)

        if self.LNotFound:
            import warnings
            txt = 'data folder(s) not found: %s' % \
                '; '.join(['"%s"->"%s"' % (dir_, key) for dir_, key in self.LNotFound])

            if False:
                raise Exception()
            else:
                warnings.warn(txt)

    def _set_data_dir(self, base_dir, key, dir_):
        """
        Search all the system paths for `dir_`,
        and set the path once it's found.

        This allows moving modules to site-packages,
        as well as using data even if the current
        working directory has changed.
        """
        found = False

        if isabs(dir_) and exists(dir_) and isdir(dir_):
            # An absolute directory
            self.D[key] = dir_
            found = True

        elif not isabs(dir_):
            # A relative directory
            t = '%s/%s' % (base_dir, dir_)

            if exists(t) and isdir(t):
                self.D[key] = t
                found = True
            else:
                t = '%s/%s' % (dirname(base_dir), dir_)
                if exists(t) and isdir(t):
                    self.D[key] = t
                    found = True

        if not found:
            self.LNotFound.append((dir_, key))

    def data_path(self, key, fnam=None):
        if fnam is None:
            return self.D[key]
        else:
            #print self.D.keys()
            return '%s/%s' % (self.D[key], fnam)
