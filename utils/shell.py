import os


class Shell:

    """ This class encapsulte all the shell command line and utilities to functions.
    """

    def __init__(self):
        pass

    @staticmethod
    def run_cmd(cmd, return_p=False):
        """
        run shell command, it return_p is True, the output will be returned
        :param cmd:
        :param return_p:
        :return:
        """
        if return_p:
            r = os.popen(cmd)
            text = r.read()
            r.close()
            return text
            # p = subprocess.Popen(cmd.split(' '), stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            # text = p.stdout.read()
            # return text
        else:
            os.system(cmd)

    @staticmethod
    def zip(folder_path, file_path):
        cmd = 'zip -q -r -o {} {}'.format(file_path, folder_path)
        Shell.run_cmd(cmd)


if __name__ == '__main__':
    #Shell.zip('/Users/tradehero/Downloads/emacs.d', '/Users/tradehero/Downloads/emacs.d.zip')
    pass

