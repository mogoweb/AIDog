package net.mogoweb.tflite.aidog;

import android.content.Context;
import android.graphics.Bitmap;
import android.graphics.BitmapFactory;
import android.os.Environment;
import android.os.SystemClock;
import android.support.test.InstrumentationRegistry;
import android.support.test.runner.AndroidJUnit4;
import android.util.Log;

import org.junit.Test;
import org.junit.runner.RunWith;

import java.io.File;
import java.io.FileNotFoundException;
import java.io.FileOutputStream;
import java.io.FileReader;
import java.io.IOException;
import java.io.LineNumberReader;

import static org.junit.Assert.*;

/**
 * Instrumented test, which will execute on an Android device.
 *
 * @see <a href="http://d.android.com/tools/testing">Testing documentation</a>
 */
@RunWith(AndroidJUnit4.class)
public class AIDogTest {
    private final static String TAG = "AIDogTest";
    @Test
    public void useAppContext() {
        // Context of the app under test.
        Context appContext = InstrumentationRegistry.getTargetContext();

        assertEquals("net.mogoweb.tflite.aidog", appContext.getPackageName());
    }

    @Test
    public void predictSingleImage() {
        File image = new File(Environment.getExternalStorageDirectory().getPath() + "/TestImages/n02085620-Chihuahua/n02085620_500.jpg");
        assertTrue(image.exists() && image.isFile());
        Bitmap bitmap = BitmapFactory.decodeFile(image.getAbsolutePath());
        Bitmap bm = Bitmap.createScaledBitmap(bitmap, ImageClassifier.DIM_IMG_SIZE_X, ImageClassifier.DIM_IMG_SIZE_Y, false);
        ImageClassifier classifier = null;
        try {
            classifier = new ImageClassifier(InstrumentationRegistry.getTargetContext());
        } catch (IOException e) {
            Log.e(TAG, "Failed to initialize an image classifier.");
            assertTrue(false);
        }

        for (int i = 0; i < 20; i++) {
            String result = classifier.classifyFrame(bm);
            Log.i(TAG, result);
        }
    }

    @Test
    public void predictImages() {
        ImageClassifier classifier = null;
        try {
            classifier = new ImageClassifier(InstrumentationRegistry.getTargetContext());
        } catch (IOException e) {
            Log.e(TAG, "Failed to initialize an image classifier.");
        }

        File imagesDirectory = new File(Environment.getExternalStorageDirectory().getPath() + "/TestImages");
        try {
            FileOutputStream resultFile = new FileOutputStream(Environment.getExternalStorageDirectory().getPath() + "/results.txt");

            if (imagesDirectory.isDirectory()) {
                for (File dir : imagesDirectory.listFiles()) {
                    if (dir.isDirectory()) {
                        String dirName = dir.getName();
                        String trueLabel = dirName.replace('-', ' ').replace('_', ' ');

                        for (File file : dir.listFiles()) {
                            String path = file.getAbsolutePath();
                            if (path.endsWith(".jpg") || path.endsWith(".jpeg") || path.endsWith(".png")) {
                                Bitmap bitmap = BitmapFactory.decodeFile(path);
                                Bitmap bm = Bitmap.createScaledBitmap(bitmap, ImageClassifier.DIM_IMG_SIZE_X, ImageClassifier.DIM_IMG_SIZE_Y, true);
                                String result = classifier.classifyBitmap(bm);
                                result = trueLabel + "_" + result;
                                resultFile.write(result.getBytes());
                            }
                        }
                    }
                }
            }
            resultFile.close();
        } catch (FileNotFoundException e) {
            e.printStackTrace();
        } catch (IOException e) {
            e.printStackTrace();
        }

        File results = new File(Environment.getExternalStorageDirectory().getPath() + "/results.txt");
        assertTrue(results.exists());
        try {
            long fileLength = results.length();
            LineNumberReader lineNumberReader = new LineNumberReader(new FileReader(results));
            lineNumberReader.skip(fileLength);
            int lines = lineNumberReader.getLineNumber();
            lineNumberReader.close();
            assertEquals(lines, 15 * 120);
        } catch (IOException e) {
            e.printStackTrace();
            assertTrue(false);
        }
    }
}
