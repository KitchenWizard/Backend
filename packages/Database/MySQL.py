###################################################################
#####   `             MySQL Manger Script                     #####
###################################################################
##### Version: 0.5                                            #####
##### Author:  Marcus R                                       #####
##### Tested:  --                                             #####
#####                                                         #####
##### Purpose: The primary purpose of this mod is to perform  #####
#####          the SQL queries to the database in one         #####
#####          location, this will help cut down on           #####
#####          duplications of mods                           #####
###################################################################

import pymysql as MySQLdb
from datetime import *
from packages.Log import kwlog
import hashlib
db = None
cursor = None


def encrypt_password(password):
    # Make password more secure
    # Return str
    kwlog.log("hashing hash")
    h = hashlib.md5()
    h.update(password)
    h.update(b"EVERYONE_LOVES_KITCHENWIZARD!")
    return h.hexdigest()


def init():
    global db
    global cursor
    db = MySQLdb.connect("localhost","kitchenWizard","","KitchenWizard")
    cursor = db.cursor()
    kwlog.log("Connected to DB")


def close():
    db.close()
    kwlog.log("DB connection closed")


def get_generic_item_list():
    sql = "SELECT GroupName FROM Grouping"
    cursor.execute(sql)
    return cursor.fetchall()


def get_session_key_expire_data(key):
    kwlog.log("Get exp date for key")
    sql = "SELECT AgeOffDate FROM Session_Key WHERE SessionKey = %s;"
    cursor.execute(sql, str(key))
    data = cursor.fetchone()
    return str(data[0])

def get_userid_from_session_key(key):
    kwlog.log("Get userid from session key")
    sql = "SELECT UserID FROM Session_Key WHERE SessionKey = %s;"
    cursor.execute(sql, key)
    data = cursor.fetchone()
    return str(data[0])


def get_product_by_barcode(barcode):
    kwlog.log("Get product by barcode")
    sql = "SELECT * FROM ProductInformation WHERE ProductID = %s;"
    cursor.execute(sql, str(barcode))
    return cursor.fetchone()


def get_group_by_name(name):
    kwlog.log("Get category by name")
    sql = "SELECT * FROM Grouping WHERE GroupName = %s;"
    cursor.execute(sql, name)
    k = cursor.fetchone()
    if not k:
        return "NONE"
    else:
        return str(k[0])


def get_inventory_list_for_user(userid):
    kwlog.log("Get items for user from DB")
    sql = "SELECT InventoryID, ProductID, ExperationDate, PercentUsed FROM Inventory WHERE UserID = %s;"
    cursor.execute(sql, userid)
    data = cursor.fetchall()
    return data


def get_password_hash_for_usr(userid):
    sql = "SELECT PasswordHash FROM Password WHERE User_id = %s;"
    cursor.execute(sql, userid)
    data = cursor.fetchone()
    return data


def is_item_in_inventory(item_id, userid):
    sql = "SELECT * FROM Inventory WHERE UserID = %s AND InventoryID = %s;"
    cursor.execute(sql, (str(userid), str(item_id)))
    data = cursor.fetchone()
    return data


def is_email_in_database(email):
    sql = "SELECT * FROM User_Information WHERE Email = %s;"
    cursor.execute(sql, email)
    data = cursor.fetchone()
    return data


def is_userid_in_DB(usr):
    sql = "SELECT UserID FROM User_Information WHERE UserID = %s;"
    cursor.execute(sql, usr)
    data = cursor.fetchone()
    return data


def put_group(name):
    kwlog.log("Put group")
    sql = "INSERT INTO `KitchenWizard`.`Grouping` (`GroupName`, `DateAdded`) VALUES (%s, %s);"
    try:
        cursor.execute(sql, (str(name), str(datetime.now())))
        db.commit()
        return True
    except:
        db.rollback()
        kwlog.log("Error adding new group")
        return False


def put_new_product(item):
    kwlog.log("Put new product")
    sql = "INSERT INTO `KitchenWizard`.`ProductInformation` (`ProductID`, `ProductName`, `ProductDiscription`, `Manufacturer`, `Quantity`) VALUES (%s, %s, %s, %s, %s);"
    try:
        cursor.execute(sql,(str(item[0]), str(item[1]), str(item[2]), str(item[3]), str(item[4])))
        db.commit()
        return True
    except:
        db.rollback()
        kwlog.log("Error adding new product")
        return False

def get_single_inventory(userid, d):
    sql = "SELECT * FROM Inventory WHERE DateAdded = %s AND UserID = %s;"
    cursor.execute(sql, (d, userid))
    return cursor.fetchone()


def put_item_in_inventory(barcode, userid):
    kwlog.log("Put item in inventory")
    sql = "INSERT INTO `KitchenWizard`.`Inventory` (`UserID`, `ProductID`, `DateAdded`) VALUES (%s, %s, %s);"
    d = str(datetime.now())
    try:
        cursor.execute(sql, (str(userid), str(barcode), d))
        db.commit()
        return get_single_inventory(userid, d)
        #return True
    except:
        db.rollback()
        kwlog.log("Error adding item to inventory")
        raise
        return False


def put_confirmation_code_in_database(code, username):
    sql = "INSERT INTO Activation_Key (Code, UserID) VALUES (%s, %s);"
    try:
        cursor.execute(sql, (str(code), str(username)))
        db.commit()
        return True
    except:
        db.rollback()
        kwlog.log("Error adding confirmation code to DB")
        return False


def put_new_account(username, fname, lname, email, hash):
    d = str(datetime.now())
    date = datetime.today()
    date = date + timedelta(6 * 30)
    hash = encrypt_password(hash)
    f_sql = "INSERT INTO User_Information (UserID, FirstName, LastName, Email, CreationDate) VALUES (%s, %s, %s, %s, %s);"
    p_sql = "INSERT INTO Password (PasswordHash, User_id, UpdatedOn) VALUES (%s, %s, %s);"
    s_sql = "INSERT INTO Session_Key (UserID, SessionKey, AgeOffDate) VALUES (%s, %s, %s);"

    try:
        cursor.execute(f_sql, (username, fname, lname, email, d))
        kwlog.log("User_Information SQL completed")
        cursor.execute(p_sql, (hash, username, d))
        kwlog.log("Password SQL completed")
        cursor.execute(s_sql, (username, '0000000', date))
        kwlog.log("Session SQL completed")
        db.commit()
        return True
    except:
        #db.rollback()
        raise
        return False


def remove_item_from_inventory(item_id):
    sql = "DELETE FROM Inventory WHERE InventoryID = %s;"
    try:
        cursor.execute(sql, (item_id))
        db.commit()
        return True
    except:
        db.rollback()
        return False


def get_group_image_by_id(group_id):
    sql = "SELECT GroupImage FROM Grouping WHERE GroupID = '%s';" % (group_id)
    cursor.execute(sql)
    data = cursor.fetchone()
    return str(data[0])


def get_active_status(username):
    sql = "SELECT IsActivated FROM User_Information WHERE UserID = %s;"
    cursor.execute(sql, username)
    return cursor.fetchone()


def update_session_key_for_usr(userid, ses):
    date = datetime.today()
    date = date + timedelta(6 * 30)
    sql = "UPDATE `KitchenWizard`.`Session_Key` SET `SessionKey`=%s, `AgeOffDate`=%s WHERE `USERID`=%s;"
    try:
        cursor.execute(sql, (ses, date, userid))
        db.commit()
        return True
    except:
        db.rollback()
        raise
        return False

def get_act_code(userid):
    sql = "SELECT Code FROM Activation_Key WHERE UserID = %s;"
    cursor.execute(sql, userid)
    data = cursor.fetchone()
    return str(data[0])


def update_activation_status_for_user(userid):
    kwlog.log("Update activation status")
    sql = "UPDATE User_Information SET IsActivated = '1' WHERE UserID = %s;"
    try:
        cursor.execute(sql, userid)
        db.commit()
        return True
    except:
        db.rollback()
        return False


def get_group_name_from_group_id(gid):
    sql = "SELECT GroupName FROM Grouping WHERE GroupID = %s;"
    cursor.execute(sql, gid)
    return cursor.fetchone()


def is_item_owned_by_user(userid, uid):
    sql = "SELECT InventoryID FROM Inventory WHERE UserID = %s AND InventoryID = %s;"
    cursor.execute(sql, (userid, uid))
    if cursor.fetchone():
        return True
    else:
        return False


def update_inventory_item(uid, info):
    sql = "UPDATE Inventory SET ExperationDate = %s, PercentUsed = %s WHERE InventoryID = %s;"
    try:
        cursor.execute(sql, (info[0], info[1], uid))
        db.commit()
        return True
    except:
        db.rollback()
        return False


def get_groups():
    sql = "SELECT GroupID, GroupName FROM Grouping;"
    cursor.execute(sql)
    return cursor.fetchall()


def get_userid_linked_to_act_code(code):
    sql="SELECT UserID FROM Activation_Key WHERE Code = %s;"
    cursor.execute(sql, code)
    data = cursor.fetchone()
    return str(data[0])


def update_first_name_for_user(userid, fname):
    sql = "UPDATE User_Information SET FirstName = %s WHERE UserID = %s;"
    try:
        cursor.execute(sql, (fname, userid))
        db.commit()
        return True
    except:
        db.rollback()
        return False


def update_last_name_for_user(userid, lname):
    sql = "UPDATE User_Information SET LastName = %s WHERE UserID = %s;"
    try:
        cursor.execute(sql, (lname, userid))
        db.commit()
        return True
    except:
        db.rollback()
        return False


def update_email_for_user(userid, email):
    sql = "UPDATE User_Information SET Email = %s WHERE UserID = %s;"
    try:
        cursor.execute(sql, (fname, email))
        db.commit()
        return True
    except:
        db.rollback()
        return False


def update_password_for_user(userid, password):
    sql = "UPDATE Password SET PasswordHash = %s, UpdatedOn = %s WHERE User_id = %s;"
    d = str(datetime.now())
    try:
        cursor.execute(sql, (password, d, userid))
        db.commit()
        return True
    except:
        db.rollback()
        return False


def is_recipe_in_db(recipeid, userid):
    sql = "SELECT * FROM Recipe WHERE UserID = %s AND RecipeID = %s;"
    cursor.execute(sql, (str(userid), str(recipeid)))
    data = cursor.fetchone()
    return data


def get_recipes_for_user(userid):
    sql = "select * from Recipe where UserID = %s"
    try:
        cursor.execute(sql, userid)
        return cursor.fetchall()
    except:
        return "Error getting recipes"


def remove_recipe_from_db(recipeId):
    kwlog.log(str(recipeId))
    sql = "DELETE FROM Recipe WHERE RecipeID = %s;"
    try:
        cursor.execute(sql, (recipeId))
        db.commit()
        return True
    except:
        raise
        db.rollback()
        return False


def insert_recipe_for_user(userid, recipe):
    d = str(datetime.now())
    sql = "INSERT INTO Recipe (Name, Discription, Image, PrepTime, CookTime, UserID, DateAdded) VALUES (%s, %s, %s, %s, %s, %s, %s);"
    try:
        cursor.execute(sql, (recipe[0], recipe[1], recipe[3], recipe[4], recipe[5], userid, d))
        db.commit()
        return True
    except:
        db.rollback()
        if kwlog.debug:
            raise
        return False


def insert_items_to_recipe(rid, items):
    for i in items:
        sql = "INSERT INTO Recipe_Item (RecipeID, GroupID, Measurment) VALUES (%s, %s, %s);"
        try:
            cursor.execute(sql, (rid, i[0], i[1]))
            db.commit()
        except:
            db.rollback()
            if kwlog.debug:
                raise
            return False
    return True


def get_recipe_id(name, userid):
    sql= "SELECT RecipeID FROM Recipe WHERE UserID = %s AND Name = %s;"
    cursor.execute(sql, (userid, name))
    return cursor.fetchone()


def get_group_by_barcode(barcode):
    sql = "SELECT GroupID FROM ProductInformation WHERE ProductID = %s;"
    cursor.execute(sql, barcode)
    data = cursor.fetchone()

    if data:
        return str(data[0])
    else:
        return "-1"


def update_group_of_item(groupid, barcode):
    sql = "UPDATE ProductInformation SET GroupID = %s WHERE ProductID = %s;"
    try:
        cursor.execute(sql, (groupid, barcode))
        db.commit()
        return True
    except:
        db.rollback()
        return False


def update_recipe_name(name, rec_id):
    sql = "UPDATE Recipe SET Name = %s WHERE RecipeID = %s;"
    kwlog.log("SQL update name request")
    try:
        cursor.execute(sql, (name, rec_id))
        db.commit()
        return True
    except:
        db.rollback()
        if kwlog.debug:
            raise
        return False

def get_ingredients_for_recipe(userid, recipeid):
    if not owned_by_user(userid, recipeid):
        if kwlog.debug:
            raise
        return "Recipe does not belong to user"
    sql = "SELECT GroupID,Measurment from Recipe_Item where recipeID = %s"
    cursor.execute(sql, (recipeid))
    data = cursor.fetchall()
    if data:
        return list(data)
    else:
        return None

def owned_by_user(userid, recId):
    sql = "SELECT * FROM Recipe WHERE UserID = %s AND RecipeID = %s;"
    cursor.execute(sql, (userid, recId))
    data = cursor.fetchone()

    if data:
        return True
    else:
        return False


def update_recipe_dis(dis, rec_id):
    sql = "UPDATE Recipe SET Discription = %s WHERE RecipeID = %s;"
    try:
        cursor.execute(sql, (dis, rec_id))
        db.commit()
        return True
    except:
        db.rollback()
        if kwlog.debug:
            raise
        return False


def update_recipe_image(image, rec_id):
    sql = "UPDATE Recipe SET Image = %s WHERE RecipeID = %s;"
    try:
        cursor.execute(sql, (image, rec_id))
        db.commit()
        return True
    except:
        db.rollback()
        if kwlog.debug:
            raise
        return False


def update_recipe_prep(prepT, rec_id):
    sql = "UPDATE Recipe SET PrepTime = %s WHERE RecipeID = %s;"
    try:
        cursor.execute(sql, (prepT, rec_id))
        db.commit()
        return True
    except:
        db.rollback()
        if kwlog.debug:
            raise
        return False


def update_recipe_cook(cookT, rec_id):
    sql = "UPDATE Recipe SET CookTime = %s WHERE RecipeID = %s;"
    try:
        cursor.execute(sql, (cookT, rec_id))
        db.commit()
        return True
    except:
        db.rollback()
        if kwlog.debug:
            raise
        return False


def update_recipe_add_item(items, rec_id):
    items = list(items)
    if insert_items_to_recipe(rec_id, items):
        return True
    else:
        if kwlog.debug:
            raise
        return False


def update_recipe_remove_item(items, rec_id):
    items = list(items)
    print(items)
    for it in items:
        sql = "DELETE FROM Recipe_Item WHERE RecipeID = %s and GroupID = %s;"
        try:
            cursor.execute(sql, (rec_id, it[0]))
            db.commit()
            return True
        except:
            db.rollback()
            if kwlog.debug:
                raise
            return False


def update_recipe_update_item(items, rec_id):
    items = list(items)
    for it in items:
        sql = "UPDATE Recipe_Item SET Measurment = %s WHERE RecipeID = %s AND GroupID = %s;"
        try:
            cursor.execute(sql, (it[1], rec_id, it[0]))
            db.commit()
            return True
        except:
            db.rollback()
            if kwlog.debug:
                raise
            return False

def remove_all_items_from_recipe(recipeid):
    sql = "DELETE FROM Recipe_Item WHERE RecipeID = %s;"
    try:
        cursor.execute(sql, (recipeid))
        db.commit()
        return True
    except:
        db.rollback()
        if kwlog.debug:
            raise
        return False

def create_new_shopping_list(name, userid):
    d = str(datetime.now())
    sql = "INSERT INTO ShoppingList (Name, UserID, DateAdded) VALUES (%s, %s, %s);"
    try:
        cursor.execute(sql, (name, userid, d))
        db.commit()
        return True
    except:
        db.rollback()
        if kwlog.debug:
            raise
        return False

def is_vaild_group(gid):
    sql = "SELECT * FROM Grouping WHERE GroupID = %s;"
    cursor.execute(sql, gid)
    data = cursor.fetchone()

    if data:
        return True
    else:
        return False


def is_vaild_shopping_list(rid, userid):
    sql = "SELECT * FROM ShoppingList WHERE ID = %s AND UserID = %s;"
    cursor.execute(sql, (rid, userid))
    data = cursor.fetchone()

    if data:
        return True
    else:
        return False


def insert_item_to_list(sid, gid, measurment, userid):
    sql = "INSERT INTO Shopping_Item (ShoppingList, GroupID, Amount) VALUES (%s, %s, %s);"
    try:
        cursor.execute(sql, (sid, gid, measurment))
        db.commit()
        return True
    except:
        db.rollback()
        if kwlog.debug:
            raise
        return False


def get_list_of_shopping_items(sid):
    print(str(sid))
    sql = "SELECT * FROM Shopping_Item WHERE ShoppingList = %s;"
    cursor.execute(sql, sid)
    return cursor.fetchall()


def get_shopping_lists(userid):
    sql = "SELECT * FROM ShoppingList WHERE UserID = %s;"
    cursor.execute(sql, userid)
    return cursor.fetchall()


def remove_item_from_shopping_list(gid, sid):
    sql = "DELETE FROM Shopping_Item WHERE ShoppingList = %s and GroupID = %s;"
    try:
        cursor.execute(sql, (sid, gid))
        db.commit()
        return True
    except:
        db.rollback()
        if kwlog.debug:
            raise
        return False


def remove_all_items_from_shopping_list(sid):
    data = get_list_of_shopping_items(sid)
    for d in data:
        if not remove_item_from_shopping_list(d[2], sid):
            return False
    return True


def remove_shopping_list(sid):
    sql = "DELETE FROM ShoppingList WHERE ID = %s;"
    try:
        cursor.execute(sql, sid)
        db.commit()
        return True
    except:
        db.rollback()
        if kwlog.debug:
            raise
        return False


def get_email_for_user(userid):
    sql = "SELECT Email FROM User_Information WHERE UserID = %s;"
    cursor.execute(sql, userid)
    return str(cursor.fetchone()[0])

def get_shopping_list_id_for_user(userid):
    sql = "SELECT ID FROM ShoppingList WHERE UserID = %s;"
    cursor.execute(sql, userid)
    k = cursor.fetchone()
    if k:
        return k[0]
    else:
        return "NONE"
