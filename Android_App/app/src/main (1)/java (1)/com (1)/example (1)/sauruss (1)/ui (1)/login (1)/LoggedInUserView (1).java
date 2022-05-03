package com.example.sauruss.ui.login;

/**
 * Class exposing authenticated user details to the UI.
 */
class LoggedInUserView {
    private String displayName;
    //... other data fields that may be accessible to the UI

    LoggedInUserView(String name) {
        this.displayName = name;
    }

    String getDisplayName() {
        return displayName;
    }
}