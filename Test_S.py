import pyodbc
#import freeple
print("start")

# conn1 = pyodbc.connect(Driver='SQL Server',
#                       Server='MAZAWEB383',
#                       Database='METSO_SOP_DEV',
#
#                       trusted_connection='yes')


connectionstring="Driver=SQL Server;Server=172.20.2.183;Database=METSO_SOP_DEV;Trusted_Connection=no;UID=Metsoadmin;PWD=Localadmin@123"
with pyodbc.connect(connectionstring, timeout=3000) as dbcon:
    print("Connected")
# SQL Server -> frepple
    with dbcon.cursor() as cursor:
      # Read items from the database, and create them in the frepple engine
      cursor.execute("SELECT  DISTINCT TOP 5 MATERIAL_CODE,MATERIAL_SHARE_OF_DPI FROM [dbo].[C_MATERIAL_DEMAND_PLAN]")
      for i in cursor.fetchall():
         print(i)
    # Plan generation
    frepple.solver_mrp(
        name="mrp",
        plantype=2,  # 1: constrained, 2: unconstrained
        constraints=0,  # Add 1 for leadtime, 2 for material, 4 for capacity, 8 for release fence
        loglevel=3,  # 0: silent, 1: log each demand, 2: verbose log, 3: extra verbose
        plansafetystockfirst=True
    ).solve()

    # frepple -> SQL Server
    with dbcon.cursor() as cursor:
        def getItems():
            for i in frepple.items():
                yield [i.name, ]


        print("Exporting")
        cursor.execute("DELETE FROM dbo.out_item")
        cursor.executemany("INSERT INTO dbo.out_item (out_name) values (?)", getItems())
        cursor.execute("commit")

print("Done")
# made change to test it for the first time
