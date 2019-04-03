package net.mogoweb.tflite.aidog;

import android.Manifest;
import android.app.Activity;
import android.content.Intent;
import android.content.pm.PackageManager;
import android.graphics.Bitmap;
import android.os.Handler;
import android.provider.MediaStore;
import android.support.annotation.NonNull;
import android.support.design.widget.Snackbar;
import android.support.v4.app.ActivityCompat;
import android.support.v7.app.AppCompatActivity;
import android.os.Bundle;
import android.text.SpannableString;
import android.text.SpannableStringBuilder;
import android.util.Log;
import android.view.View;
import android.widget.Button;
import android.widget.RadioButton;
import android.widget.TextView;

import java.io.IOException;

public class MainActivity extends AppCompatActivity
        implements ActivityCompat.OnRequestPermissionsResultCallback {
    private static final int REQUEST_CAMERA = 0;
    private static final int SELECT_FILE = 1;

    private static final int DEVICE_CPU = 0;
    private static final int DEVICE_GPU = 1;

    private static final int PERMISSION_REQUEST_CAMERA = 0;

    private static final String TAG = "AIDog";

    private ImageClassifier classifier;

    private TextView tvResult;

    private View mLayout;

    private int mDevice = DEVICE_CPU;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_main);
        mLayout = findViewById(R.id.container);

        Button btnTakePhoto = (Button)findViewById(R.id.btnTakePhoto);
        btnTakePhoto.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View view) {
                // Check if the Camera permission has been granted
                if (ActivityCompat.checkSelfPermission(MainActivity.this, Manifest.permission.CAMERA)
                        == PackageManager.PERMISSION_GRANTED) {
                    // Permission is already available, start camera
                    cameraIntent();
                } else {
                    // Permission is missing and must be requested.
                    requestCameraPermission();
                }
            }
        });
        Button btnSelectPhoto = (Button)findViewById(R.id.btnSelectPhoto);
        btnSelectPhoto.setOnClickListener(new View.OnClickListener() {
            @Override
            public void onClick(View view) {
                boolean result = Utility.checkPermission(MainActivity.this);
                if (result)
                    galleryIntent();
            }
        });
        tvResult = (TextView)findViewById(R.id.tvResult);

        try {
            classifier = new ImageClassifier(this);
        } catch (IOException e) {
            Log.e(TAG, "Failed to initialize an image classifier.");
        }
    }

    /**
     * Requests the {@link android.Manifest.permission#CAMERA} permission.
     * If an additional rationale should be displayed, the user has to launch the request from
     * a SnackBar that includes additional information.
     */
    private void requestCameraPermission() {
        // Permission has not been granted and must be requested.
        if (ActivityCompat.shouldShowRequestPermissionRationale(this,
                Manifest.permission.CAMERA)) {
            // Provide an additional rationale to the user if the permission was not granted
            // and the user would benefit from additional context for the use of the permission.
            // Display a SnackBar with cda button to request the missing permission.
            Snackbar.make(mLayout, R.string.camera_access_required,
                    Snackbar.LENGTH_INDEFINITE).setAction(R.string.ok, new View.OnClickListener() {
                @Override
                public void onClick(View view) {
                    // Request the permission
                    ActivityCompat.requestPermissions(MainActivity.this,
                            new String[]{Manifest.permission.CAMERA},
                            PERMISSION_REQUEST_CAMERA);
                }
            }).show();

        } else {
            // Request the permission. The result will be received in onRequestPermissionResult().
            ActivityCompat.requestPermissions(this,
                    new String[]{Manifest.permission.CAMERA}, PERMISSION_REQUEST_CAMERA);
        }
    }

    private void cameraIntent()
    {
        Intent intent = new Intent(MediaStore.ACTION_IMAGE_CAPTURE);
        startActivityForResult(intent, REQUEST_CAMERA);
    }

    private void galleryIntent()
    {
        Intent intent = new Intent();
        intent.setType("image/*");
        intent.setAction(Intent.ACTION_GET_CONTENT); //
        startActivityForResult(Intent.createChooser(intent, "Select File"), SELECT_FILE);
    }

    @Override
    public void onRequestPermissionsResult(int requestCode, @NonNull String[] permissions,
                                           @NonNull int[] grantResults) {
        // BEGIN_INCLUDE(onRequestPermissionsResult)
        if (requestCode == PERMISSION_REQUEST_CAMERA) {
            // Request for camera permission.
            if (grantResults.length == 1 && grantResults[0] == PackageManager.PERMISSION_GRANTED) {
                // Permission has been granted. Start camera.
                cameraIntent();
            } else {
                // Permission request was denied.
                Snackbar.make(mLayout, R.string.camera_permission_denied,
                        Snackbar.LENGTH_SHORT)
                        .show();
            }
        }
        // END_INCLUDE(onRequestPermissionsResult)
    }

    @Override
    public void onActivityResult(int requestCode, int resultCode, Intent data) {
        super.onActivityResult(requestCode, resultCode, data);
        if (resultCode == Activity.RESULT_OK) {
            if (requestCode == SELECT_FILE)
                onSelectFromGalleryResult(data);
            else if (requestCode == REQUEST_CAMERA)
                onCaptureImageResult(data);
        }
    }

    public void onRadioButtonClicked(View view) {
        // Is the button now checked?
        boolean checked = ((RadioButton) view).isChecked();

        // Check which radio button was clicked
        switch (view.getId()) {
            case R.id.opt_cpu:
                if (checked && mDevice != DEVICE_CPU) {
                    mDevice = DEVICE_CPU;
                    updateActiveModel();
                }
                break;
            case R.id.opt_gpu:
                if (checked && mDevice != DEVICE_GPU) {
                    mDevice = DEVICE_GPU;
                    updateActiveModel();
                }
                break;
        }
    }

    private void updateActiveModel() {
        // Disable classifier while updating
        if (classifier != null) {
            classifier.close();
            classifier = null;
        }

        Log.i(TAG, "Changing device to " + (mDevice == 0 ? "CPU" : "GPU"));

        // Try to load model.
        try {
            classifier = new ImageClassifier(this);
        } catch (IOException e) {
            Log.e(TAG, "Failed to initialize an image classifier.");
        }

        // Customzie the interpreter to the type of device we want to use.
        if (mDevice == DEVICE_CPU) {
        } else if (mDevice == DEVICE_GPU) {
            if (!GpuDelegateHelper.isGpuDelegateAvailable()) {
                showToast("gpu not in this build.");
                classifier = null;
            } else {
                classifier.useGpu();
            }
        }
    }

    /**
     * Shows a {@link Toast} on the UI thread for the classification results.
     *
     * @param s The message to show
     */
    private void showToast(String s) {
        SpannableStringBuilder builder = new SpannableStringBuilder();
        SpannableString str1 = new SpannableString(s);
        builder.append(str1);
        showToast(builder);
    }

    private void showToast(final SpannableStringBuilder builder) {
        runOnUiThread(
                new Runnable() {
                    @Override
                    public void run() {
                        tvResult.setText(builder, TextView.BufferType.SPANNABLE);
                    }
                });
    }

    @SuppressWarnings("deprecation")
    private void onSelectFromGalleryResult(Intent data) {
        if (data != null) {
            try {
                Bitmap bitmap = MediaStore.Images.Media.getBitmap(getApplicationContext().getContentResolver(), data.getData());
                Bitmap bm = Bitmap.createScaledBitmap(bitmap, ImageClassifier.DIM_IMG_SIZE_X, ImageClassifier.DIM_IMG_SIZE_Y, false);
                String textToShow = classifier.classifyFrame(bm);
                tvResult.setText(textToShow);
            } catch (IOException e) {
                e.printStackTrace();
            }
        }
    }

    private void onCaptureImageResult(Intent data) {
        Bitmap bm = (Bitmap) data.getExtras().get("data");

        String textToShow = classifier.classifyFrame(bm);
        tvResult.setText(textToShow);
    }

}
