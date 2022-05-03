package com.example.sauruss.ui.dashboard;

import android.Manifest;
import android.app.Activity;
import android.content.pm.PackageManager;
import android.os.Build;
import android.os.Bundle;
import android.util.Log;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.AdapterView;
import android.widget.ArrayAdapter;
import android.widget.Button;
import android.widget.Spinner;
import android.widget.TextView;
import android.widget.Toast;

import androidx.annotation.NonNull;
import androidx.annotation.Nullable;
import androidx.annotation.RequiresApi;
import androidx.core.app.ActivityCompat;
import androidx.fragment.app.Fragment;
import androidx.lifecycle.Observer;
import androidx.lifecycle.ViewModelProvider;

import com.budiyev.android.codescanner.CodeScanner;
import com.budiyev.android.codescanner.CodeScannerView;
import com.budiyev.android.codescanner.DecodeCallback;
import com.example.sauruss.R;
import com.example.sauruss.UserInfo;
import com.google.gson.Gson;
import com.google.zxing.Result;

import org.json.JSONArray;
import org.json.JSONException;
import org.json.JSONObject;

import java.io.BufferedInputStream;
import java.io.BufferedReader;
import java.io.IOException;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.net.HttpURLConnection;
import java.net.MalformedURLException;
import java.net.URL;
import java.net.URLConnection;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;

public class DashboardFragment extends Fragment {

    private DashboardViewModel dashboardViewModel;

    @Override
    public View onCreateView(@NonNull LayoutInflater inflater,
                             ViewGroup container, Bundle savedInstanceState) {

        List<String> listaMACaddress = new ArrayList<>();
        View root = inflater.inflate(R.layout.fragment_dashboard, container, false);
        dashboardViewModel =
                new ViewModelProvider(this).get(DashboardViewModel.class);
        final TextView textView = root.findViewById(R.id.text_dashboard);

        dashboardViewModel.getText().observe(getViewLifecycleOwner(), new Observer<String>() {
            @Override
            public void onChanged(@Nullable String s) {
                textView.setText(s);
            }
        });

        if (ActivityCompat.checkSelfPermission(getContext(), Manifest.permission.CAMERA) != PackageManager.PERMISSION_GRANTED) {
            requestPermissions(new String[]{Manifest.permission.CAMERA}, 1);
        }
        ScanFunction(inflater,container,savedInstanceState,listaMACaddress,root);

        Spinner spinner_x = (Spinner) root.findViewById(R.id.spinner_x);
        Spinner spinner_y = (Spinner) root.findViewById(R.id.spinner_y);
        // Spinner click listener
        spinner_x.setOnItemSelectedListener(new AdapterView.OnItemSelectedListener() {
            public void onItemSelected(AdapterView<?> parent, View view,
                                       int position, long id) {
                String item_x = parent.getItemAtPosition(position).toString();
                UserInfo.setItemx(item_x);
                //Toast.makeText(parent.getContext(), "Selected: " + item_x, Toast.LENGTH_LONG).show();

            }

            @Override
            public void onNothingSelected(AdapterView<?> parent) {

            }
        });
        spinner_y.setOnItemSelectedListener(new AdapterView.OnItemSelectedListener() {
            public void onItemSelected(AdapterView<?> parent, View view,
                                       int position, long id) {
                String item_y = parent.getItemAtPosition(position).toString();
                UserInfo.setItemy(item_y);
                //Toast.makeText(parent.getContext(), "Selected: " + item_y, Toast.LENGTH_LONG).show();

            }
            @Override
            public void onNothingSelected(AdapterView<?> parent) {

            }
        });

        // Spinner Drop down elements
        List<String> categories = new ArrayList<>();

        for(int i=50;i<=500;i++){
                categories.add(String.valueOf(i));
        }

        // Creating adapter for spinner
        ArrayAdapter<String> dataAdapter = new ArrayAdapter<String>(getActivity(), android.R.layout.simple_spinner_item, categories);

        // Drop down layout style - list view with radio button
        dataAdapter.setDropDownViewResource(android.R.layout.simple_spinner_dropdown_item);

        // attaching data adapter to spinner
        spinner_x.setAdapter(dataAdapter);
        spinner_y.setAdapter(dataAdapter);


        Button done_button = (Button) root.findViewById(R.id.done);
        done_button.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View root) {

                Thread t = new Thread( new Runnable() {
                    @Override
                    public void run() {
                        try {
                            dbCall(UserInfo.getMAC(),UserInfo.getItemx(),UserInfo.getItemy());
                            Log.e("item x",UserInfo.getItemx());
                            Log.e("item y",UserInfo.getItemy());

                        } catch (IOException e) {
                            e.printStackTrace();
                        }
                    }
                }); t.start();
            }

        });

        return root;
    }
    /**
     * configures position of sensors and saves them on db associated to theid ID(mac)
     * @param mac adress scanned
     * @param x,y relative positions of sensor from base along x and y axes
     * @throws IOException
     */
    public static void dbCall(String mac,String x, String y) throws IOException {

        String urlString = "" + mac +"/"+ x +"/"+ y +"/";

        URL url = new URL(urlString);

        Log.v("URL",urlString);
        HttpURLConnection httpURLConnection = (HttpURLConnection) url.openConnection();
        httpURLConnection.setRequestMethod("POST");
        httpURLConnection.setDoOutput(true);

        httpURLConnection.setRequestProperty("Cookie", UserInfo.getAccessToken());
        httpURLConnection.setRequestProperty("Content-Type", "application/json");

        Log.d("dentro DBCALL", httpURLConnection.getResponseCode() + " " + httpURLConnection.getResponseMessage());

    }


    public void ScanFunction(@NonNull LayoutInflater inflater,
                             ViewGroup container, Bundle savedInstanceState, List lista, View root) {
        Log.e("scan function", "inside");

        final Activity activity = getActivity();

        CodeScannerView scannerView = root.findViewById(R.id.scanner_view);
        CodeScanner mCodeScanner = new CodeScanner(activity, scannerView);

        mCodeScanner.setDecodeCallback(new DecodeCallback() {
            //@Override
            public void onDecoded(@NonNull final Result result) {
                activity.runOnUiThread(new Runnable() {
                    @Override
                    public void run() {

                        if (!lista.contains(result.getText())){
                            lista.add(result.getText());
                        }
                        Toast.makeText(activity, result.getText(), Toast.LENGTH_SHORT).show();
                        UserInfo.setMAC(result.getText());

                        // TODO: add post request che manda mac address
                        Thread thread = new Thread(new Runnable() {

                            @RequiresApi(api = Build.VERSION_CODES.O)
                            @Override
                            public void run() {

                                String response = "";
                                BufferedReader reader = null;
                                HttpURLConnection httpURLConnection = null;
                                //String username = UserInfo.getUsername();
                                //String password = UserInfo.getPassword();
                                String myserver = "";

                                URL url = null;
                                try {
                                    //TODO: in future implementations 1/1/ will be latitude and longitude of the sensor whose mac is being scanned
                                    url = new URL(myserver + "/sensors/" + result.getText() + "/1/1/");

                                    httpURLConnection = (HttpURLConnection) url.openConnection();
                                    httpURLConnection.setRequestMethod("POST");
                                    httpURLConnection.setDoOutput(true);

                                    httpURLConnection.setRequestProperty("Cookie", UserInfo.getAccessToken());
                                    httpURLConnection.setRequestProperty("Content-Type", "application/json");

                                    Log.e("bhu", httpURLConnection.getRequestProperty("Cookie"));
                                    Log.d(" qr response:", httpURLConnection.getResponseCode() + " " + httpURLConnection.getResponseMessage());
                                    if (httpURLConnection.getResponseCode()== 200){
                                        UserInfo.setQrmessage("MAC inviato");
                                    }else if(httpURLConnection.getResponseCode()== 500){
                                        UserInfo.setQrmessage("MAC già presente");}
                                    else{
                                        UserInfo.setQrmessage("invio MAC non riuscito");
                                    }
                                    getActivity().runOnUiThread(new Runnable() {
                                        @Override
                                        public void run() {
                                            Toast.makeText(getActivity(),
                                                    UserInfo.getQrmessage(), Toast.LENGTH_SHORT).show();
                                        }
                                    });

                                } catch (MalformedURLException e) {
                                    e.printStackTrace();
                                } catch (IOException e) {
                                    e.printStackTrace();
                                }
                            }
                        });
                        thread.start();

                    }
                });


            }
        });

        scannerView.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View view) {
                mCodeScanner.startPreview();
            }
        });
    }

}