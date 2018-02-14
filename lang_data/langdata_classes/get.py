def get(D, default, L):
    for key in L:
        assert isinstance(D, dict)

        if isinstance(key, (list, tuple)):
            found = False
            for i_key in key:
                if i_key in D:
                    found = True
                    D = D[i_key]
                    break

            if not found and default==KeyError:
                print D
                raise KeyError(key)
            elif not found:
                return default
        else:
            if default!=KeyError and not key in D:
                return default
            D = D[key]
    return D
