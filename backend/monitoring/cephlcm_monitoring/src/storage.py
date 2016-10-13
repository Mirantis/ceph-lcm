import json
import os.path


class RawResultStorage(object):
    def __init__(self, root):
        self._root = root
        self._all = None

    def _load(self):
        if self._all is None:
            self._all = {}
            rt = os.path.abspath(self._root)
            for fname in os.listdir(rt):
                if fname.startswith('.'):
                    continue

                full_path = os.path.join(rt, fname)

                if '.' in fname:
                    fname_no_ext, ext = fname.rsplit('.', 1)
                    self._all[fname_no_ext] = (True, ext, full_path)
                else:
                    self._all[fname] = (False, None, full_path)

        return self._all

    def __getattr__(self, name):
        self._load()

        path = os.path.join(self._root, name)
        if os.path.isdir(path):
            return True, None, self.__class__(path)

        if name in self._all:
            is_file, ext, full_path = self._all[name]
            setattr(self, name, (is_file, ext, full_path))

            if is_file:
                data = open(full_path, 'rb').read()
                return ext != 'err', ext, data
            else:
                return True, None, self.__class__(full_path)

        raise AttributeError(
            "No storage for {0!r} found. Have only '{1}' attrs".format(name, ",".join(self)))

    def __iter__(self):
        return iter(self._load().keys())

    def __getitem__(self, path):
        if '/' not in path:
            return getattr(self, path)

        item, rest = path.split('/', 1)
        is_ok, ext, data = getattr(self, item)
        if not is_ok:
            raise KeyError("error in path")
        if ext is not None:
            raise KeyError("Path not found")
        return data[rest]

    def get(self, path, default=None, expected_format='txt'):
        try:
            ok, frmt, data = self[path]
        except AttributeError:
            return default

        if not ok or frmt != expected_format:
            return default

        return data

    def __len__(self):
        return len(self._load())


class JResultStorage(object):
    def __init__(self, storage):
        self.__storage = storage
        self.__dct = []

    def __getattr__(self, name):
        is_ok, ext, data = getattr(self.__storage, name)

        if not is_ok:
            raise AttributeError("{0!r} contains error".format(name))
        elif ext is None:
            return self.__class__(data)
        elif ext != 'json':
            raise AttributeError("{0!r} have type {1!r}, not json".format(name, ext))

        res = json.loads(data)
        setattr(self, name, res)
        return res

    def get(self, path, default=None, expected_format='json'):
        res = self.__storage.get(path, default, expected_format=expected_format)
        if res is not None:
            return json.loads(res)
        return res

    def __iter__(self):
        return iter(self.__storage)

    def __getitem__(self, path):
        if path not in self.__dct:
            is_ok, ext, data = self.__storage[path]

            if not is_ok:
                raise KeyError("{0!r} contains error".format(path))

            elif ext != 'json':
                raise KeyError("{0!r} have type {1!r}, not json".format(path, ext))

            self.__dct[path] = json.loads(data)
        return self.__dct[path]

    def __len__(self):
        return len(self.__storage)
