import librosa
import numpy as np

#Yes this code is AI. No I don't have any clue as to what it does or how. Something about samples and cosine or crap

def load_audio_features(file_path):
    y, sr = librosa.load(file_path, sr=22050, mono=True)  # standardize sample rate & mono
    mfcc = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13)
    # Normalize for comparison
    mfcc = mfcc / np.linalg.norm(mfcc)
    return mfcc

def compare_audio_perceptual(file1, file2, threshold=0.95):
    mfcc1 = load_audio_features(file1)
    mfcc2 = load_audio_features(file2)
    
    min_frames = min(mfcc1.shape[1], mfcc2.shape[1])
    mfcc1 = mfcc1[:, :min_frames]
    mfcc2 = mfcc2[:, :min_frames]
    # Compute similarity (cosine similarity)
    similarity = np.dot(mfcc1.flatten(), mfcc2.flatten())
    
    #print(f"Similarity: {similarity:.4f}")
    print(similarity)
    if similarity > threshold:
        return True
    else:
        return False
