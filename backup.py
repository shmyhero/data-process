from dataaccess.rawfilemgr import RawFileMgr


def clean_obsoleted_data():
    RawFileMgr().clean_obsoleted_data()


def backup_daily_data():
    RawFileMgr().backup()


def main():
    backup_daily_data()
    clean_obsoleted_data()


if __name__ == '__main__':
    main()




