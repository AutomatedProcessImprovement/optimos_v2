import { Asset, AssetType } from "../redux/slices/assetsSlice";
import JSZip, { JSZipObject } from "jszip";
import { timetableSchema } from "../validation/timetableSchema";
import { constraintsSchema } from "../validation/constraintsSchema";
import * as uuid from "uuid";
import { ConstraintsType, TimetableType } from "../redux/slices/optimosApi";

export const unzipFile = async (file: File): Promise<[Asset[], string[]]> => {
  const zip = await new JSZip().loadAsync(file);
  const files = zip.files;

  const assets = [];

  const errors: string[] = [];

  for (const [filename, file] of Object.entries(files)) {
    try {
      const asset = await fileToAsset(file);
      if (asset) {
        assets.push(asset);
      }
    } catch (e) {
      errors.push(`Error parsing ${filename}: ${e}`);
    }
  }
  return [assets, errors];
};

const isZipObj = (file: File | JSZipObject): file is JSZipObject =>
  "dir" in file;

export const fileToAsset = async (
  file: File | JSZipObject
): Promise<Asset | undefined> => {
  const isDir = isZipObj(file) ? file.dir : false;
  const filename = file.name;

  if (isDir) return;
  // We match the file extension to determine before we read the file,
  // to speed up the process and avoid reading binary files.
  if (!filename.match(/\.(bpmn|json|yaml)$/i)) {
    throw new Error(`Unknown file type: ${filename}`);
  }

  const content = isZipObj(file) ? await file.async("text") : await file.text();

  if (filename.endsWith(".bpmn")) {
    return {
      id: uuid.v4(),
      name: filename,
      type: AssetType.BPMN,
      value: content,
    };
  } else if (filename.endsWith(".json")) {
    var parsedJson;
    try {
      parsedJson = parseJson(content);
    } catch (e) {
      throw Error(`Error parsing ${filename}: ${e}`);
    }
    if (timetableSchema.isValidSync(parsedJson)) {
      return {
        id: uuid.v4(),
        name: filename,
        type: AssetType.TIMETABLE,
        value: parsedJson as TimetableType,
      };
    } else if (constraintsSchema.isValidSync(parsedJson)) {
      return {
        id: uuid.v4(),
        name: filename,
        type: AssetType.OPTIMOS_CONSTRAINTS,
        value: parsedJson as ConstraintsType,
      };
    } else {
      console.log(timetableSchema.validateSync(parsedJson));
      throw new Error(`Unknown JSON file: ${filename}`);
    }
  }
};
export const parseJson = (content: string) => {
  content = content.replace(/(?!")Infinity(?!")/g, '"Infinity"');
  content = content.replace(/(?!")NaN(?!")/g, '"NaN"');
  return JSON.parse(content);
};
