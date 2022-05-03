package com.example.sauruss;

import android.app.Application;

public class UserInfo extends Application {

    private static String username;
    private static String password;
    private static String token;
    private static String imgname;
    private static String videoname;
    private static String qrmessage;
    private static String notification;
    private static String alarms;
    private static String log;
    private static String dash;
    private static String item_y;
    private static String item_x;
    private static String mac;



    @Override
    public void onCreate() {
        super.onCreate();
        username="";
        password="";
        token="";
        imgname="";
        videoname="";
        notification="";
        alarms="";
        log="";
        item_x="";
        item_y = "";
        mac = "";
    }

    public static String getUsername() {
        return username;
    }

    public static void setUsername(String username) {
        UserInfo.username = username;
    }

    public static String getPassword() {
        return password;
    }

    public static void setPassword(String password) {
        UserInfo.password = password;
    }

    public static String getAccessToken() {
        return token;
    }

    public static void setAccessToken(String token) {
        String[] parts = token.split(";", 2);
        String cookie = parts[0];
        cookie =cookie.substring(1);
        UserInfo.token = cookie;
    }

    public static String getVideoName() {
        String[] f = videoname.split("/");
        return f[1];
    }
    public static String getImgName() {
        String[] f = imgname.split("/");
        return f[1];
    }

    public static void setImgName(String filename) {
        UserInfo.imgname = filename;
    }
    public static void setVideoName(String filename) {
        UserInfo.videoname = filename;
    }

    public static String getQrmessage() {
        return qrmessage;
    }

    public static void setQrmessage(String qr) {
        UserInfo.qrmessage = qr;
    }

    public static String getNotification() {
        return notification;
    }

    public static void setNotification(String qr) {
        UserInfo.notification = qr;
    }


    public static void setAlarms(String qr) {
        UserInfo.alarms = qr;
    }
    public static String getAlarms() {
        return alarms;
    }

    public static void setLogin(String log){
        UserInfo.log = log;
    }
    public static String getLogin(){ return log;}

    //public static void setDash(String dash) { UserInfo.dash = dash;    }
    //public static String getDash() {        return dash;    }

    public static void setItemy(String item) {
        UserInfo.item_x = item;
    }
    public static String getItemy() {
        return item_y;
    }

    public static void setItemx(String item) {
        UserInfo.item_y = item;
    }
    public static String getItemx() {
        return item_x;
    }

    public static void setMAC(String item) {
        UserInfo.mac = item;
    }
    public static String getMAC() {
        return mac;
    }

}