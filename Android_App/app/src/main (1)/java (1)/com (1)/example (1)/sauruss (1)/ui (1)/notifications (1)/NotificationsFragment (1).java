package com.example.sauruss.ui.notifications;

import android.Manifest;
import android.content.pm.PackageManager;
import android.graphics.Bitmap;
import android.graphics.BitmapFactory;
import android.net.Uri;
import android.os.Bundle;
import android.os.Environment;
import android.util.Log;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.Button;
import android.widget.ImageView;
import android.widget.MediaController;

import androidx.annotation.NonNull;
import androidx.annotation.Nullable;
import androidx.core.app.ActivityCompat;
import androidx.fragment.app.Fragment;
import androidx.lifecycle.ViewModelProvider;

import com.example.sauruss.R;
import com.example.sauruss.UserInfo;

import android.widget.Toast;
import android.widget.VideoView;

import org.json.JSONArray;
import org.json.JSONException;
import org.json.JSONObject;

import java.io.BufferedReader;
import java.io.File;
import java.io.FileOutputStream;
import java.io.IOException;
import java.io.InputStream;
import java.io.InputStreamReader;
import java.net.HttpURLConnection;
import java.net.MalformedURLException;
import java.net.URL;


public class NotificationsFragment extends Fragment {

    private NotificationsViewModel notificationsViewModel;

    private static final int BUFFER_SIZE = 4096;
    String nome_video = "";
    String nome_img = "";

    String saveDir = Environment.getExternalStorageDirectory().getAbsolutePath() + "/DCIM/Camera/";

    @Override
    public void onCreate(@Nullable Bundle savedInstanceState) {

        super.onCreate(savedInstanceState);
        if (ActivityCompat.checkSelfPermission(getContext(), Manifest.permission.READ_EXTERNAL_STORAGE) != PackageManager.PERMISSION_GRANTED
                && ActivityCompat.checkSelfPermission(getContext(), Manifest.permission.WRITE_EXTERNAL_STORAGE) != PackageManager.PERMISSION_GRANTED) {
            //requestPermissions(new String[]{Manifest.permission.READ_EXTERNAL_STORAGE}, 1);
            requestPermissions(new String[]{Manifest.permission.WRITE_EXTERNAL_STORAGE}, 1);
        }
        //TODO:se non funziona splittare in due thread
        Thread t = new Thread(new Runnable() {
            @Override
            public void run() {

                nome_img = getFileName(0);
                nome_video = getFileName(1);

                UserInfo.setVideoName(nome_video);
                UserInfo.setImgName(nome_img);

                //getAlarms();
                //nomefile = fromTimestampCreatePath(t);
                Log.e("PATH IMG", nome_img);
                Log.e("PATH VIDEO", nome_video);
                if (nome_video!="") {
                    String fileURL_video = "" + nome_video + ".mp4";
                    try {
                        downloadFile(fileURL_video, saveDir);
                    } catch (IOException e) {
                        e.printStackTrace();
                    }
                }
                if (nome_img!="") {
                    String fileURL_img = "" + nome_img + ".png";
                    try {
                        downloadFile(fileURL_img, saveDir);
                    } catch (IOException e) {
                        e.printStackTrace();
                    }
                }

            }
        });
        t.start();
    }

    public View onCreateView(@NonNull LayoutInflater inflater,
                             ViewGroup container, Bundle savedInstanceState) {
        notificationsViewModel =
                new ViewModelProvider(this).get(NotificationsViewModel.class);

        View view = inflater.inflate(R.layout.fragment_notifications, container, false);

        Button show_video = (Button) view.findViewById(R.id.show_video);
        show_video.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                if(UserInfo.getAlarms() == "off"){
                    getActivity().runOnUiThread(new Runnable() {
                        @Override
                        public void run() {
                            Toast.makeText(getActivity(),
                                    "video non disponibile", Toast.LENGTH_SHORT).show();
                        }
                    });
                }else {
                    VideoView video = (VideoView) view.findViewById(R.id.videoview);

                    String videopath = saveDir + UserInfo.getVideoName() + ".mp4";

                    video.setVideoURI(Uri.parse(videopath));

                    video.setMediaController(new MediaController(getActivity()));

                    video.requestFocus();
                    video.start();
                }
            }
        });

        Button show_img = (Button) view.findViewById(R.id.show_img);
        show_img.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View v) {
                if(UserInfo.getAlarms() == "off"){

                        getActivity().runOnUiThread(new Runnable() {
                            @Override
                            public void run() {
                                Toast.makeText(getActivity(),
                                        "Immagine non disponibile", Toast.LENGTH_SHORT).show();
                            }
                        });
                 
                }else {

                    File imgFile = new File(saveDir + UserInfo.getImgName() + ".png");
                    Log.v("btn img", "cliccato");
                    if (imgFile.exists()) {
                        Log.v("msg", "img esiste");

                        Bitmap myBitmap = BitmapFactory.decodeFile(imgFile.getAbsolutePath());

                        ImageView myImage = (ImageView) view.findViewById(R.id.item_image_view);

                        myImage.setImageBitmap(myBitmap);

                    }
                }
            }
        });


        return view;
    }

    /**
     * Downloads a file from a URL
     * @param fileURL HTTP URL of the file to be downloaded
     * @param saveDir path of the directory to save the file
     */
    public static void downloadFile(String fileURL, String saveDir) throws IOException {
        Log.e("filepath", saveDir);
        Log.e("URL??",fileURL);

        URL url = new URL(fileURL);
        HttpURLConnection httpConn = (HttpURLConnection) url.openConnection();
        httpConn.setRequestMethod("GET");
        httpConn.setRequestProperty("Cookie", UserInfo.getAccessToken());

        int responseCode = httpConn.getResponseCode();

        // always check HTTP response code first
        if (responseCode == HttpURLConnection.HTTP_OK) {
            String fileName = "";
            String disposition = httpConn.getHeaderField("Content-Disposition");
            String contentType = httpConn.getContentType();
            int contentLength = httpConn.getContentLength();

            if (disposition != null) {
                // extracts file name from header field
                int index = disposition.indexOf("filename=");
                if (index > 0) {
                    fileName = disposition.substring(index + 10,
                            disposition.length() - 1);
                }
            } else {
                // extracts file name from URL
                fileName = fileURL.substring(fileURL.lastIndexOf("/") + 1,
                        fileURL.length());
            }

            System.out.println("Content-Type = " + contentType);
            System.out.println("Content-Disposition = " + disposition);
            System.out.println("Content-Length = " + contentLength);
            System.out.println("fileName = " + fileName);

            // opens input stream from the HTTP connection
            InputStream inputStream = httpConn.getInputStream();
            String saveFilePath = saveDir + File.separator + fileName;

            // opens an output stream to save into file
            FileOutputStream outputStream = new FileOutputStream(saveFilePath);

            int bytesRead = -1;
            byte[] buffer = new byte[BUFFER_SIZE];
            while ((bytesRead = inputStream.read(buffer)) != -1) {
                outputStream.write(buffer, 0, bytesRead);
            }

            outputStream.close();
            inputStream.close();

            System.out.println("File downloaded");
            UserInfo.setNotification("file downloaded");

        } else {
            System.out.println("No file to download. Server replied HTTP code: " + responseCode);
            UserInfo.setNotification("No file to download");
        }
        httpConn.disconnect();
    }

    /**
     * gets the id of the sensor that sent the alarm
     * and use this to retrieve the filename of video/img captured by the drone
     * @param integer (0 = img or 1=video) to retrieve  the video or img name
     */
    public static String getFileName(Integer integer) {
        String tms = "";
        String sensorID = "";
        try {

            StringBuilder result = new StringBuilder();
            URL url = null;
            // to retrieve info about which sensor triggered an alarm
            url = new URL("") ;

            HttpURLConnection conn = (HttpURLConnection) url.openConnection();
            conn.setRequestMethod("GET");
            conn.setRequestProperty("Cookie", UserInfo.getAccessToken());

            BufferedReader rd = new BufferedReader(new InputStreamReader(conn.getInputStream()));
            String line;
            while ((line = rd.readLine()) != null) {
                result.append(line);
            }
            rd.close();
            JSONObject obj = new JSONObject(String.valueOf(result));
            // t = obj.getJSONObject("Timestamps").getString("timestamp");
            //if (obj.keys(result.).length === 0

            JSONArray arr = obj.getJSONArray("Alarms"); // notice that `"posts": [...]`
            Log.v("GET ALARMS",result.toString());
            if (arr.length()==0 || arr==null){
                Log.e("ALARM", "db empty");
                UserInfo.setAlarms("off");
                return "";
            }
            else {
                sensorID = arr.getJSONObject(integer).getString("sensor_id");
                Log.v("json sensorID", sensorID);
            }
        } catch (MalformedURLException e) {
            e.printStackTrace();
        } catch (IOException e) {
            e.printStackTrace();
        } catch (JSONException e) {
            e.printStackTrace();
        }

        try {

            StringBuilder result = new StringBuilder();
            URL url = null;
            url = new URL(""+ sensorID + "/");

            HttpURLConnection conn = (HttpURLConnection) url.openConnection();
            conn.setRequestMethod("GET");
            conn.setRequestProperty("Cookie", UserInfo.getAccessToken());

            BufferedReader rd = new BufferedReader(new InputStreamReader(conn.getInputStream()));
            String line;
            while ((line = rd.readLine()) != null) {
                result.append(line);
            }
            rd.close();

            JSONObject obj = new JSONObject(String.valueOf(result));

            JSONArray arr = obj.getJSONArray("Timestamps");
            tms = arr.getJSONObject(integer).getString("timestamp");

            Log.v("GET ALARMS",result.toString());
            Log.v("json sensorID", sensorID);
            //ret = fromTimestampCreatePath(tms);
            Log.v("timestamp", tms);
        } catch (MalformedURLException e) {
            e.printStackTrace();
        } catch (IOException e) {
            e.printStackTrace();
        } catch (JSONException e) {
            e.printStackTrace();
        }
        return fromTimestampCreatePath(tms);
    }

    public static String fromTimestampCreatePath(String t){
        String[] nw = t.split(" ");
        String d = nw[0];
        String o = nw[1];

        String[] data = d.split("-");
        String aa = data[0].substring(2);
        String mm = data[1];
        String gg = data [2];

        String ggmmaa = (new StringBuilder()).append(gg).append(mm).append(aa).toString();

        String ora = o.replace(":","");
        String path_to_file = ggmmaa +"/"+ ora;
        Log.e("path???",path_to_file);
        return path_to_file;
    }

}
