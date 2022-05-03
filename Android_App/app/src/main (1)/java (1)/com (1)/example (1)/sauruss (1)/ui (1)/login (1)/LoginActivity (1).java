package com.example.sauruss.ui.login;

import android.app.Activity;

import androidx.lifecycle.Observer;
import androidx.lifecycle.ViewModelProvider;

import android.content.Intent;
import android.os.Bundle;

import androidx.annotation.Nullable;
import androidx.annotation.StringRes;
import androidx.appcompat.app.AppCompatActivity;

import android.text.Editable;
import android.text.TextWatcher;
import android.util.Log;
import android.view.KeyEvent;
import android.view.View;
import android.view.inputmethod.EditorInfo;
import android.widget.Button;
import android.widget.EditText;
import android.widget.ProgressBar;
import android.widget.TextView;
import android.widget.Toast;

import com.example.sauruss.MainActivity;
import com.example.sauruss.R;
import com.example.sauruss.UserInfo;

import java.io.BufferedReader;
import java.net.HttpURLConnection;
import java.net.URL;

public class LoginActivity extends AppCompatActivity {

    private LoginViewModel loginViewModel;
    String username="";
    String psw="";
    String token="";
    String MESSAGE ="";

    @Override
    public void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_login);
        loginViewModel = new ViewModelProvider(this, new LoginViewModelFactory())
                .get(LoginViewModel.class);

        final EditText usernameEditText = findViewById(R.id.username);
        final EditText passwordEditText = findViewById(R.id.password);
        final Button loginButton = findViewById(R.id.login);
        final ProgressBar loadingProgressBar = findViewById(R.id.loading);
        UserInfo.setLogin("no");

        loginViewModel.getLoginFormState().observe(this, new Observer<LoginFormState>() {
            @Override
            public void onChanged(@Nullable LoginFormState loginFormState) {
                if (loginFormState == null) {
                    return;
                }
                loginButton.setEnabled(loginFormState.isDataValid());
                if (loginFormState.getUsernameError() != null) {
                    usernameEditText.setError(getString(loginFormState.getUsernameError()));
                }
                if (loginFormState.getPasswordError() != null) {
                    passwordEditText.setError(getString(loginFormState.getPasswordError()));
                }
            }
        });

        loginViewModel.getLoginResult().observe(this, new Observer<LoginResult>() {
            @Override
            public void onChanged(@Nullable LoginResult loginResult) {
                if (loginResult == null) {
                    return;
                }
                loadingProgressBar.setVisibility(View.GONE);
                if (loginResult.getError() != null) {
                    showLoginFailed(loginResult.getError());
                }
                if (loginResult.getSuccess() != null ){
                   updateUiWithUser(loginResult.getSuccess());
                }
                setResult(Activity.RESULT_OK);

                //Complete and destroy login activity once successful
                finish();
            }
        });

        TextWatcher afterTextChangedListener = new TextWatcher() {
            @Override
            public void beforeTextChanged(CharSequence s, int start, int count, int after) {
                // ignore
            }

            @Override
            public void onTextChanged(CharSequence s, int start, int before, int count) {
                // ignore
            }

            @Override
            public void afterTextChanged(Editable s) {
                loginViewModel.loginDataChanged(usernameEditText.getText().toString(),
                        passwordEditText.getText().toString());
            }
        };
        usernameEditText.addTextChangedListener(afterTextChangedListener);
        passwordEditText.addTextChangedListener(afterTextChangedListener);
        passwordEditText.setOnEditorActionListener(new TextView.OnEditorActionListener() {

            @Override
            public boolean onEditorAction(TextView v, int actionId, KeyEvent event) {
                if (actionId == EditorInfo.IME_ACTION_DONE) {
                    loginViewModel.login(usernameEditText.getText().toString(),
                            passwordEditText.getText().toString());
                }
                return false;
            }
        });

        loginButton.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                loadingProgressBar.setVisibility(View.VISIBLE);
                username = usernameEditText.getText().toString();
                psw =  passwordEditText.getText().toString();
                loginViewModel.login(usernameEditText.getText().toString(),
                        passwordEditText.getText().toString());
                Log.v(username, psw);

                //PostAsync task = new PostAsync(getApplicationContext());
                //task.execute();
                // TODO : implement post request login here
                Thread thread = new Thread(new Runnable() {

                    @Override
                    public void run() {
                        String string = "";
                        String response = "";
                        BufferedReader reader = null;
                        HttpURLConnection httpURLConnection = null;
                        HttpURLConnection httpURLConnection_reg = null;

                        try {
                            URL url = new URL("" + username + "/" + psw + "/");

                            httpURLConnection = (HttpURLConnection) url.openConnection();

                            httpURLConnection.setRequestMethod("POST");
                            httpURLConnection.setDoOutput(true);
                            httpURLConnection.setRequestProperty("Content-Type", "application/json");


                            if (httpURLConnection.getResponseCode() == 200) {
                                string = httpURLConnection.getHeaderFields().get("Set-Cookie").toString();
                                UserInfo.setAccessToken(string);
                                Log.v("cooooookie??", UserInfo.getAccessToken());
                                showToast("Welcome back "+ UserInfo.getUsername()+ "!");
                                UserInfo.setLogin("yes");

                            }else{
                                URL url1 = new URL(""+username+"/"+psw+"/"+"userphonediprova/");

                                httpURLConnection_reg = (HttpURLConnection) url1.openConnection();
                                httpURLConnection_reg.setRequestMethod("POST");
                                httpURLConnection_reg.setDoOutput(true);
                                httpURLConnection_reg.setRequestProperty("Content-Type", "application/json");
                                Log.d("registration response", String.valueOf(httpURLConnection_reg.getResponseCode()));

                                if (httpURLConnection_reg.getResponseCode() == 200){
                                    UserInfo.setLogin("yes");

                                    string = httpURLConnection_reg.getHeaderFields().get("Set-Cookie").toString();
                                    UserInfo.setAccessToken(string);
                                    Log.v("cooki on reg??", UserInfo.getAccessToken());

                                    showToast("Welcome "+ UserInfo.getUsername()+ "!");
                                    //String welcome = "Welcome " + UserInfo.getUsername() + "!";
                                    //Toast.makeText(getApplicationContext(), welcome, Toast.LENGTH_LONG).show();


                                    //Toast.makeText(LoginActivity.this, "Login and Registration failed", Toast.LENGTH_SHORT).show();
                                }else {
                                    String MESSAGE= "Sorry! Registration or login failed, retry";
                                    showToast(MESSAGE);
                                    UserInfo.setLogin("no");

                                    Intent MainIntent = new Intent(LoginActivity.this, LoginActivity.class);
                                    finish();
                                    overridePendingTransition( 0, 0);
                                    startActivity(MainIntent);
                                    overridePendingTransition( 0, 0);

                                }

                            }

                        } catch (Exception e) {
                            e.printStackTrace();
                            Log.d("Error", "error");
                        } finally {
                            try {
                                reader.close();
                                if (httpURLConnection != null) {
                                    httpURLConnection.disconnect();
                                }
                            } catch (Exception ex) {
                            }
                        }

                        Log.d("RESPONSE POST", response);
                        //return response;
                    }
                });
                thread.start();
            }


        });
    }

    private void updateUiWithUser(LoggedInUserView model) {
        //String welcome = "Welcome " + this.username + "!";
        //Toast.makeText(getApplicationContext(), welcome, Toast.LENGTH_LONG).show();
        // TODO:(done) initiate successful logged in experience
        Intent MainIntent = new Intent(LoginActivity.this, MainActivity.class);
        startActivity(MainIntent);
    }

    private void showLoginFailed(@StringRes Integer errorString) {
        Toast.makeText(getApplicationContext(), errorString, Toast.LENGTH_SHORT).show();
    }

    public void showToast(final String toast)
    {
        runOnUiThread(() -> Toast.makeText(LoginActivity.this, toast, Toast.LENGTH_SHORT).show());
    }
}